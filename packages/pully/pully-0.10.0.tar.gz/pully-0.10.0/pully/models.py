# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import enum

import msgspec

from .pullyfile import PullyProject


class ResultStatus(enum.Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"


class Result(msgspec.Struct, frozen=True):
    status: ResultStatus
    project: PullyProject
