# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities.run._base.entity import Run

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_flower.entities.run._base.spec import RunSpecFlowerRun
    from digitalhub_runtime_flower.entities.run._base.status import RunStatusFlowerRun


class RunFlowerRun(Run):
    """
    RunFlowerRun class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecFlowerRun,
        status: RunStatusFlowerRun,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecFlowerRun
        self.status: RunStatusFlowerRun
