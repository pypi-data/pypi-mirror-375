# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.entity.metadata import Metadata

from digitalhub_runtime_flower.entities.function._base.entity import FunctionFlower
from digitalhub_runtime_flower.entities.function.flower_client.spec import FunctionSpecFlowerClient
from digitalhub_runtime_flower.entities.function.flower_client.status import FunctionStatusFlowerClient


class FunctionFlowerClient(FunctionFlower):
    """
    FunctionFlowerClient class.
    """

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: FunctionSpecFlowerClient,
        status: FunctionStatusFlowerClient,
        user: str | None = None,
    ) -> None:
        super().__init__(project, name, uuid, kind, metadata, spec, status, user)

        self.spec: FunctionSpecFlowerClient
        self.status: FunctionStatusFlowerClient
