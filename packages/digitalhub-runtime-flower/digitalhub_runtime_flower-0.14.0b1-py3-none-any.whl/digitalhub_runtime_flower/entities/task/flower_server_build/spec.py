# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Optional

from digitalhub.entities.task._base.spec import TaskSpec, TaskValidator


class TaskSpecFlowerServerBuild(TaskSpec):
    """
    TaskSpecFlowerServerBuild specifications.
    """

    def __init__(
        self,
        instructions: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.instructions = instructions


class TaskValidatorFlowerServerBuild(TaskValidator):
    """
    TaskValidatorFlowerServerBuild validator.
    """

    instructions: Optional[list[str]] = None
