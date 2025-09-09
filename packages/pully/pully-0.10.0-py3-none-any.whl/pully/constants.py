# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

BASE_DIR = Path.cwd()

PACKAGE_DIR = Path(__file__).parent.absolute()

CLI_DIR = PACKAGE_DIR / "cli"

CLI_COMMANDS = sorted(
    [path.stem for path in CLI_DIR.glob("*.py") if not path.stem.startswith("_")]
)

PULLY_FILE_NAME = ".pully.json"

PULLY_LOG = ".pully.log"
