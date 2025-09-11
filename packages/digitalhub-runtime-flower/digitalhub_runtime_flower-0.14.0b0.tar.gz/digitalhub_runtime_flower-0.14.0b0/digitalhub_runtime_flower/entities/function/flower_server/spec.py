# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub_runtime_flower.entities.function._base.spec import FunctionSpecFlower, FunctionValidatorFlower


class FunctionSpecFlowerServer(FunctionSpecFlower):
    """
    FunctionSpecFlowerServer specifications.
    """

    def __init__(
        self,
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


class FunctionValidatorFlowerServer(FunctionValidatorFlower):
    """
    FunctionValidatorFlowerServer validator.
    """
