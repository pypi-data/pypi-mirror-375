# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import subprocess
from pathlib import Path

from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR
from ..pullyfile import PullyProject
from ._options import add_path_prefix_argument


def clone_project(config_dir: Path, project: PullyProject):
    repo_dir = config_dir / project.local_path
    repo_dir.mkdir(exist_ok=True, parents=True)
    print(
        colored("cloning", "green"),
        project.local_path,
        colored(f"({project.project_id})", "green"),
    )
    try:
        subprocess.run(
            ["git", "clone", project.ssh_url, repo_dir],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            colored("failed", "yellow"),
            project.local_path,
            colored("(git error)", "yellow"),
        )


def fetch_project(config_dir: Path, project: PullyProject):
    repo_dir = config_dir / project.local_path
    print(
        colored("fetching", "green"),
        project.local_path,
        colored(f"({project.project_id})", "green"),
    )
    try:
        subprocess.run(
            ["git", "fetch"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            colored("failed", "yellow"),
            project.local_path,
            colored("(git error)", "yellow"),
        )


def pull_project(config_dir: Path, project: PullyProject):
    git_dir = config_dir / project.local_path / ".git"
    if git_dir.exists():
        fetch_project(config_dir, project)
    else:
        clone_project(config_dir, project)


def pull_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR
    with pullyfile.project_context(base_dir, search=not args.directory) as context:
        config_dir, projects, groups = context
        for project_id, project in projects.items():
            if args.path_prefix and not project.local_path.startswith(args.path_prefix):
                continue
            pull_project(config_dir, project)


def pull_command_parser(subparsers):
    parser = subparsers.add_parser("pull")
    parser.set_defaults(func=pull_command)

    add_path_prefix_argument(parser)
