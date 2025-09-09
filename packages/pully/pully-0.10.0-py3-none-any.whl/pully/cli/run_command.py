# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR, PULLY_LOG
from ..models import Result, ResultStatus
from ..pullyfile import PullyProject
from ._options import add_path_prefix_argument


def run_process(command: List[str], repo_dir: Path, stdout, stderr, env=None):
    subprocess.run(
        command,
        cwd=repo_dir,
        text=True,
        check=True,
        stdout=stdout,
        stderr=stderr,
        env=env,
    )


def run_process_in_project(
    config_dir: Path,
    project: PullyProject,
    log_path: Path,
    command: List[str],
) -> Result:
    repo_dir = config_dir / project.local_path

    env = os.environ.copy()
    env["PULLY_PROJECT_PATH"] = project.local_path
    env["PULLY_PROJECT_FULL_PATH"] = repo_dir

    if not repo_dir.exists():
        print(
            colored("skipping", "yellow"),
            f"{repo_dir} not found, run pull to clone project",
        )
        return Result(status=ResultStatus.SKIPPED, project=project)
    try:
        if log_path:
            with open(log_path, "a") as output_stream:
                output_stream.write(f"\n--------- {project.local_path} ---------\n")
                output_stream.flush()
                run_process(
                    command, repo_dir, output_stream, subprocess.STDOUT, env=env
                )
                return Result(status=ResultStatus.SUCCEEDED, project=project)
        else:
            width, _ = shutil.get_terminal_size((80, 20))
            headline = (
                colored("running", "green") + " " + colored(project.local_path, "white")
            )
            lines = width - len(f"running {project.local_path}") - 1
            print(headline, "-" * lines)
            run_process(command, repo_dir, None, None, env=env)
            return Result(status=ResultStatus.SUCCEEDED, project=project)
    except subprocess.CalledProcessError:
        print(
            colored("failed", "red"),
            project.local_path,
        )
        return Result(status=ResultStatus.FAILED, project=project)


def resolve_executable_path(path: Path) -> Path:
    """
    Resolve an executable path both inside and outside of PATH.
    """
    try:
        return str(Path(shutil.which(path)).absolute())
    except TypeError:
        raise FileNotFoundError(path)


def build_pully_run_command(args, input_file=sys.stdin) -> List[str]:
    """
    Build fully-qualified subprocess arguments from args/command options.
    """
    if args.args:
        prog = resolve_executable_path(args.args[0])
        return [prog, *args.args[1:]]

    elif args.command:
        if args.command == "-":
            return [*args.entrypoint, input_file.read().rstrip()]
        return [*args.entrypoint, args.command]

    raise NotImplementedError("reached impossible parser state")


def run_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR

    command = build_pully_run_command(args)

    results = []

    start_time = datetime.utcnow()

    with pullyfile.project_context(base_dir, search=not args.directory) as context:
        config_dir, projects, groups = context
        if args.output == "pully-log":
            log_path = config_dir / PULLY_LOG
        else:
            log_path = None
        for project_id, project in projects.items():
            if args.path_prefix and not project.local_path.startswith(args.path_prefix):
                continue

            if args.output == "project-log":
                log_path = config_dir / project.local_path / PULLY_LOG
            result = run_process_in_project(config_dir, project, log_path, command)
            results.append(result)

    end_time = datetime.utcnow()

    succeeded = [
        result for result in results if result.status == ResultStatus.SUCCEEDED
    ]
    failed = [result for result in results if result.status == ResultStatus.FAILED]
    skipped = [result for result in results if result.status == ResultStatus.SKIPPED]

    print(
        "\n{}: {}, {}: {}, {}: {}, {}: {}".format(
            colored("time", "white", attrs=["bold"]),
            str(end_time - start_time).split(".")[0],
            colored("succeeded", "green"),
            len(succeeded),
            colored("failed", "red"),
            len(failed),
            colored("skipped", "yellow"),
            len(skipped),
        )
    )


def run_command_parser(subparsers):
    parser = subparsers.add_parser("run")
    parser.set_defaults(func=run_command)
    parser.add_argument(
        "-o",
        "--output",
        choices=["show", "pully-log", "project-log"],
        default="show",
        help=(
            "What to do with command output. "
            "show to display in terminal, "
            "pully-log to add output to .pully.log, "
            "project-log to add output to .pully.log file in each repo"
        ),
    )
    parser.add_argument(
        "-e",
        "--entrypoint",
        type=json.loads,
        default=["/bin/sh", "-euc"],
        help="command entrypoint",
    )

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "-c",
        "--command",
        help="command string to execute. If '-', commands are read from stdin",
    )
    actions.add_argument("args", nargs="*", default=[], metavar="ARGS")

    add_path_prefix_argument(parser)
