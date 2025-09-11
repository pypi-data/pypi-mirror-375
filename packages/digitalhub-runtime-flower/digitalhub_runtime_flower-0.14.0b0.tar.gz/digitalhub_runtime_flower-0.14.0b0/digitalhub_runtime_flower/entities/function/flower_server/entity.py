# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.entity.metadata import Metadata

from digitalhub_runtime_flower.entities.function._base.entity import FunctionFlower
from digitalhub_runtime_flower.entities.function.flower_server.spec import FunctionSpecFlowerServer
from digitalhub_runtime_flower.entities.function.flower_server.status import FunctionStatusFlowerServer


class FunctionFlowerServer(FunctionFlower):
    """
    FunctionFlowerServer class.
    """

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: FunctionSpecFlowerServer,
        status: FunctionStatusFlowerServer,
        user: str | None = None,
    ) -> None:
        super().__init__(project, name, uuid, kind, metadata, spec, status, user)

        self.spec: FunctionSpecFlowerServer
        self.status: FunctionStatusFlowerServer
