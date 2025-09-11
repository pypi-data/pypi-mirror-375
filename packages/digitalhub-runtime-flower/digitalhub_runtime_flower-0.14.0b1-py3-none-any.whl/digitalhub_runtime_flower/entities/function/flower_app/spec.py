# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub_runtime_flower.entities.function._base.spec import FunctionSpecFlower, FunctionValidatorFlower
from digitalhub_runtime_flower.entities.function.flower_app.models import FABSource


class FunctionSpecFlowerApp(FunctionSpecFlower):
    """
    FunctionSpecFlowerApp specifications.
    """

    def __init__(
        self,
        fab_source: dict | None = None,
        image: str | None = None,
        base_image: str | None = None,
        requirements: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            image=image,
            base_image=base_image,
            requirements=requirements,
            **kwargs,
        )
        self.fab_source = fab_source


class FunctionValidatorFlowerApp(FunctionValidatorFlower):
    """
    FunctionValidatorFlowerApp validator.
    """

    fab_source: Optional[FABSource] = None
