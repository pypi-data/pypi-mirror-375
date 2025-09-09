from __future__ import annotations
import sys
import os
import json
import time
import fnmatch
import shutil
import subprocess
import shlex
import logging
from datetime import datetime
from pathlib import Path
from typing import (
    Sequence,
    TextIO,
    Iterable,
    NamedTuple,
    Optional,
    Iterator,
    List,
    Literal,
    get_args,
)
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

if sys.version_info >= (3, 11):
    from typing import assert_never
else:
    from typing_extensions import assert_never

import click

USAGE = """\
reminders-sink is a script that takes other scripts as input
and runs them in parallel. The exit code of each script it runs determines what
reminder-sink does:

\b
0: I've done this task recently, no need to warn
2: I haven't done this task recently, print the script name
3: I haven't done this task recently, print the output of the script
Anything else: Fatal error

You can set the REMINDER_SINK_PATH environment variable to a colon-delimited
list of directories that contain reminder-sink jobs. For example, in your shell
profile, set:

\b
export REMINDER_SINK_PATH="${HOME}/.local/share/reminder-sink:${HOME}/Documents/reminder-sink"

This scans the directories for executables and runs them in parallel. A script is
considered enabled if it is executable or if the file name ends with '.enabled'.
"""


INTERPRETER = os.environ.get("REMINDER_SINK_DEFAULT_INTERPRETER", "bash")


def is_executable(path: str) -> bool:
    return os.access(path, os.X_OK)


Result = tuple[str, int, str]
IGNORE_FILES = {"__pycache__", ".git", ".mypy_cache", ".pytest_cache", ".stignore"}


cache_dir = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
silent_file_location = cache_dir / "reminder-sink-silent.txt"
if "REMINDER_SINK_SILENT_FILE" in os.environ:
    silent_file_location = Path(os.environ["REMINDER_SINK_SILENT_FILE"])
silent_file_location = silent_file_location.expanduser().absolute()


def silenced_line_is_active(line: str, curtime: int) -> Optional[str]:
    """
    parses a line that looks like:

    name_of_script:1698097637
    where the number is when the script expires
    """
    match, _, epoch = line.partition(":")
    if not epoch.isnumeric():
        logging.warning(f"Failed to parse integer from line: {line}")
        return None
    try:
        expired_at = int(epoch)
    except ValueError:
        logging.warning(f"Failed to parse integer from line: {line}")
        return None
    if curtime > expired_at:
        logging.debug(
            f"{match} expired at {expired_at} ({datetime.fromtimestamp(expired_at)}), skipping..."
        )
        return None
    return match


class SilentFile(NamedTuple):
    file: Path

    def load(self) -> Iterator[str]:
        if not self.file.exists():
            logging.debug(f"{self.file} does not exist, skipping SilentFile load")
            return
        curtime = int(time.time())
        for line in self.file.open("r"):
            if ls := line.strip():
                if active := silenced_line_is_active(ls, curtime):
                    logging.debug(f"active silencer: {repr(active)}")
                    yield active

    # silenced does not include all lines in the file, just
    # the ones which are active (that have not expired yet)
    def autoprune(self, *, silenced: List[str]) -> None:
        # if there are items in the file that have expired, skip truncating
        if len(silenced) > 0:
            logging.debug(f"{self.file} has active silencers, skipping auto-prune")
            return

        # read the file, check if its already empty
        # if its not, unlink the file
        if not self.file.exists():
            logging.debug(f"{self.file} does not exist, skipping auto-prune")
            return

        contents = self.file.read_text()
        # if the user left it there and its empty, leave it
        if contents.strip() == "":
            logging.debug(f"{self.file} is empty, skipping auto-prune")
            return

        # instead of unlinking, we should just write an empty file.
        # it doesn't change much for this (just the read of the empty file),
        # but makes things like syncing changes using syncthing/rsync more consistent
        logging.debug(f"{self.file} has no active silencers, truncating file")
        self.file.write_bytes(b"")

    def add_to_file(self, name: str, duration: int) -> None:
        if ":" in name:
            raise ValueError("pattern to silence cannot contain ':'")
        if name.strip() == "":
            raise ValueError("no text passed as input pattern")
        with self.file.open("a") as f:
            # add the duration to the current time, that is when this expires
            f.write(f"{name}:{int(time.time() + duration)}\n")

    @staticmethod
    def is_silenced(name: str, *, silenced: List[str]) -> bool:
        return any(fnmatch.fnmatch(name, active) for active in silenced)


class Script(NamedTuple):
    path: Path
    enabled: bool

    @property
    def name(self) -> str:
        return self.path.stem

    def detect_shebang(self) -> Optional[str]:
        with open(self.path) as f:
            first_line = f.readline()
        if first_line.startswith("#!"):
            interp = first_line[2:].strip()
            # remove /usr/bin/env, its looked up in PATH anyways
            if interp.startswith("/usr/bin/env "):
                interp = interp[len("/usr/bin/env ") :]
            # if it was misconfigured/empty, don't use it
            if interp.strip():
                return interp
        return None

    def run(self) -> Result:
        name = self.name
        start = time.perf_counter()
        interp = self.detect_shebang() or INTERPRETER
        args = [*shlex.split(interp), str(self.path)]
        logging.debug(f"{name}: Starting '{' '.join(args)}'")
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        exitcode = proc.wait()

        output = proc.stdout.read() if proc.stdout else ""

        assert proc.stderr is not None, "stderr should be a pipe"
        for line in proc.stderr:
            logging.debug(f"{name}: {line.rstrip()}")

        logging.debug(
            f"{name}: (took {round(time.perf_counter() - start, 5)}) with exit code {exitcode} and output {repr(output.strip())}"
        )
        return name, exitcode, output


def script_is_enabled(path: Path) -> bool:
    return path.name.endswith(".enabled") or is_executable(str(path))


def find_execs(exclude: List[str]) -> Iterable[Script]:
    dirs = os.environ.get("REMINDER_SINK_PATH")
    if not dirs:
        click.echo(
            "The REMINDER_SINK_PATH environment variable is not set. "
            "It should contain a colon-delimited list of directories "
            "that contain reminder-sink jobs. "
            "For example, in your shell profile, set:\n"
            'export REMINDER_SINK_PATH="${HOME}/.local/share/reminder-sink:${HOME}/data/reminder-sink"',
            err=True,
        )
        return
    for d in dirs.split(":"):
        if not d.strip():
            continue
        logging.debug(f"reminder-sink: Searching {d}")
        if not os.path.isdir(d):
            click.echo(f"Error: {d} is not a directory", err=True)
            continue
        for file in os.listdir(d):
            if os.path.basename(file) in IGNORE_FILES:
                continue
            abspath_f = Path(os.path.abspath(os.path.join(d, file)))
            for pattern in exclude:
                if fnmatch.fnmatch(str(abspath_f), pattern):
                    logging.debug(f"reminder-sink: matched {pattern}, skipping {file}")
                    break
            else:
                yield Script(path=abspath_f, enabled=script_is_enabled(abspath_f))

        logging.debug(f"reminder-sink: finished searching {d}")


def run_parallel_scripts(
    executables: Iterable[Script],
    cpu_count: int,
) -> Iterable[Future[Result]]:
    logging.debug(f"reminder-sink: Running scripts with {cpu_count} threads")
    with ThreadPoolExecutor(max_workers=cpu_count) as executor:
        for script in executables:
            if not script.enabled:
                logging.debug(f"{script.name}: not enabled")
                continue
            yield executor.submit(script.run)


def parse_result(res: Result) -> List[str]:
    name, exitcode, output = res
    match exitcode:
        case 0:
            pass
        case 2:
            return [name]
        case 3:
            return output.strip().splitlines()
        case _:
            logging.error(
                f"{name}: exited with non-(0,2,3) exit code. Pass --debug or set REMINDER_SINK_DEBUG=1 to see output"
            )
    return []


def write_results(
    futures: Iterable[Future[Result]],
    /,
    *,
    files: Sequence[TextIO],
    silenced: List[str],
) -> None:
    logging.debug(f"{silenced=}")
    for future in as_completed(futures):
        if lines := parse_result(future.result()):
            for line in lines:
                if not SilentFile.is_silenced(line, silenced=silenced):
                    for f in files:
                        f.write(f"{line}\n")


FORMAT = "%(asctime)s %(levelname)s - %(message)s"


@click.group(
    help=USAGE,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="See https://github.com/purarue/reminder-sink for more information",
)
@click.option(
    "-d",
    "--debug",
    envvar="REMINDER_SINK_DEBUG",
    show_default=True,
    show_envvar=True,
    is_flag=True,
    help="print debug information",
)
def main(debug: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=FORMAT)


OutputFormat = Literal["repr", "path", "json"]


@main.command(short_help="list all scripts", name="list")
@click.option(
    "-e", "--enabled", is_flag=True, default=False, help="only list enabled scripts"
)
@click.option(
    "-E",
    "--exclude",
    type=str,
    multiple=True,
    help="exclude scripts matching this pattern",
)
@click.option(
    "-o",
    "--output-format",
    type=click.Choice(get_args(OutputFormat)),
    help="what to print",
    default=get_args(OutputFormat)[0],
    show_default=True,
)
def _list(output_format: OutputFormat, enabled: bool, exclude: Sequence[str]) -> None:
    """
    List all scripts found in REMINDER_SINK_PATH
    """
    scripts = list(find_execs(list(exclude)))
    if enabled:
        scripts = list(filter(lambda s: s.enabled, scripts))
    for s in scripts:
        match output_format:
            case "path":
                click.echo(s.path)

            case "repr":
                click.echo(str(s))

            case "json":
                click.echo(json.dumps({"path": str(s.path), "enabled": s.enabled}))

            case format:
                assert_never(format)


@main.command(short_help="test a script", name="test")
@click.argument("SCRIPT", type=click.Path(exists=True, dir_okay=False))
def _test(script: str) -> None:
    """
    Tests a script by running it once and printing the output
    """
    click.echo(f"Testing {script}", err=True)
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    name, exitcode, output = Script(path=Path(script), enabled=True).run()
    click.echo(f"Finished {name} with exit code {exitcode} and output {repr(output)}")
    exit(exitcode)


@main.command(short_help="toggle a script", name="toggle")
@click.argument("SCRIPT", type=click.Path(exists=True, dir_okay=False))
def _toggle(script: str) -> None:
    """
    If the script is enabled, disable it, and vice versa

    This renames the file to/from .enabled
    and toggles executable permissions
    """
    scp = Path(script).absolute()
    is_enabled = script_is_enabled(scp)

    sc_str = str(scp)
    if is_enabled:
        click.echo("Was enabled, disabling...", err=True)
        if is_executable(sc_str):
            click.echo("Removing executable permissions...", err=True)
            os.chmod(sc_str, 0o644)
        if sc_str.endswith(".enabled"):
            click.echo("Removing '.enabled' suffix...", err=True)
            os.rename(sc_str, sc_str[: -len(".enabled")])
    else:
        click.echo("Was disabled, enabling...", err=True)
        if not is_executable(sc_str):
            click.echo("Adding executable permissions...", err=True)
            os.chmod(sc_str, 0o755)
        if sc_str.endswith(".enabled"):
            pass
        elif sc_str.endswith(".disabled"):
            click.echo("Removing '.disabled' suffix...", err=True)
            os.rename(sc_str, sc_str[: -len(".disabled")] + ".enabled")
        else:
            click.echo("Adding '.enabled' suffix...", err=True)
            os.rename(sc_str, sc_str + ".enabled")


@main.command(short_help="run all scripts in parallel")
@click.option(
    "-c",
    "--cpu-count",
    show_default=True,
    type=int,
    help="number of threads to use",
    default=os.cpu_count(),
)
@click.option(
    "-f",
    "--file",
    type=click.File("w"),
    envvar="REMINDER_SINK_OUTPUT_FILE",
    show_envvar=True,
    default=None,
    help="additional file to write results to",
)
@click.option(
    "-E",
    "--exclude",
    type=str,
    multiple=True,
    help="exclude scripts matching this pattern",
)
@click.option(
    "-a",
    "--autoprune",
    is_flag=True,
    default=False,
    help="automatically remove silenced file if none are active",
)
def run(cpu_count: int, file: TextIO, autoprune: bool, exclude: Sequence[str]) -> None:
    """
    Run all scripts in parallel, print the names of the scripts which
    have expired
    """
    sf = SilentFile(Path(silent_file_location))
    silenced: List[str] = list(sf.load())
    if autoprune:
        sf.autoprune(silenced=silenced)

    files = [sys.stdout]
    if file is not None:
        if file.name == "<stdout>":
            click.echo(
                "This already writes to STDOUT ('-'), -f/--file is to specify another file",
                err=True,
            )
        else:
            files.append(file)

    logging.debug(f"Writing to [{', '.join(f.name for f in files)}]")

    write_results(
        run_parallel_scripts(find_execs(list(exclude)), cpu_count=cpu_count),
        files=files,
        silenced=silenced,
    )
    for f in files:
        f.flush()


@main.group(name="silence", short_help="temporarily silence a reminder")
def _silence() -> None:
    """
    Silences a reminder for some duration

    This can be useful to ignore a reminder temporarily without modifying
    the underlying mechanism to check for the reminder

    To change the location of the file where this stores silenced reminders,
    you can set the REMINDER_SINK_SILENT_FILE envvar
    """
    pass


@_silence.command(name="add", short_help="silence a reminder")
@click.option(
    "-d",
    "--duration",
    default=86400,
    help="number of seconds to silence this reminder for [default: 86400 (1 day)]",
    type=int,
)
@click.argument("NAME")
def _silence_add(duration: int, name: str) -> None:
    """
    This allows you to pass a unix-like glob (uses the fnmatch module) for the name

    \b
    You could also use 'reminder-sink run' itself with fzf to select one, like:

    reminder-sink silence add "$(reminder-sink run | fzf)"
    """
    sf = SilentFile(Path(silent_file_location))
    try:
        sf.add_to_file(name=name, duration=duration)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@_silence.command(name="list", short_help="list silenced reminders")
def _silence_list() -> None:
    """
    Lists active silenced reminders
    """
    sf = SilentFile(Path(silent_file_location))
    for line in sf.load():
        click.echo(line)


def get_editor_path() -> str:
    """
    returns editor specified by $EDITOR, $VISUAL, else uses a list of fallbacks
    """
    editors = ["nano", "nvim", "vim"]
    for envvar in ("EDITOR", "VISUAL"):
        if envvar in os.environ:
            editors.insert(0, os.environ[envvar])
    for editor in editors:
        if location := shutil.which(editor):
            return location
    else:
        raise RuntimeError(
            "No editor found, please set the EDITOR or VISUAL environment variable"
        )


@_silence.command(name="edit", short_help="edit silenced reminder file")
def _silence_edit() -> None:
    """
    Edit the file which contains the silenced reminders in your editor
    """
    subprocess.call([get_editor_path(), str(silent_file_location)])


@_silence.command(name="reset", short_help="reset all silenced reminders")
@click.option(
    "-f",
    "--if-expired",
    is_flag=True,
    default=False,
    help="only reset if all silenced reminders have expired",
)
def _silence_reset(if_expired: bool) -> None:
    """
    Resets all silenced reminders
    """
    sf = SilentFile(Path(silent_file_location))
    if if_expired:
        silenced = list(sf.load())
        sf.autoprune(silenced=silenced)
    else:
        # write an empty file
        sf.file.write_bytes(b"")


@_silence.command(name="file", short_help="print location of silenced reminders file")
def _silence_file() -> None:
    """
    Prints the location of the silenced reminders file
    """
    click.echo(silent_file_location)


if __name__ == "__main__":
    main(prog_name="reminder-sink")
