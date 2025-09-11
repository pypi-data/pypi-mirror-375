# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_flower.entities.function._base.entity import FunctionFlower

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_flower.entities.function.flower_app.spec import FunctionSpecFlowerApp
    from digitalhub_runtime_flower.entities.function.flower_app.status import FunctionStatusFlowerApp


class FunctionFlowerApp(FunctionFlower):
    """
    FunctionFlowerApp class.
    """

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: FunctionSpecFlowerApp,
        status: FunctionStatusFlowerApp,
        user: str | None = None,
    ) -> None:
        super().__init__(project, name, uuid, kind, metadata, spec, status, user)

        self.spec: FunctionSpecFlowerApp
        self.status: FunctionStatusFlowerApp
