# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities.run._base.entity import Run

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

from digitalhub_runtime_flower.entities.run.flower_server_deploy.spec import RunSpecFlowerServerDeploy
from digitalhub_runtime_flower.entities.run.flower_server_deploy.status import RunStatusFlowerServerDeploy


class RunFlowerServerDeploy(Run):
    """
    RunFlowerServerDeploy class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecFlowerServerDeploy,
        status: RunStatusFlowerServerDeploy,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecFlowerServerDeploy
        self.status: RunStatusFlowerServerDeploy
