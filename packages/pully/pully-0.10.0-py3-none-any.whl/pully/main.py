# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
from importlib import import_module

from ._version import __version__
from .constants import CLI_COMMANDS


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-C",
        "--directory",
        type=str,
        help="directory with pully projects",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(required=True)

    for command_name in CLI_COMMANDS:
        command = import_module(f".{command_name}", "pully.cli")
        getattr(command, f"{command_name}_parser")(subparsers=subparsers)

    return parser


def parse_args(args=None):
    parser = get_parser()
    return parser.parse_args(args=args)


def main():
    parser = get_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except FileNotFoundError as excinfo:
        parser.error(f"file not found: {excinfo}")
