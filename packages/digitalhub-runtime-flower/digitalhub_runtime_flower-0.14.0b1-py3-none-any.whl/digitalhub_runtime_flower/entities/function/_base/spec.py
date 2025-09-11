# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub.entities.function._base.spec import FunctionSpec, FunctionValidator


class FunctionSpecFlower(FunctionSpec):
    """
    FunctionSpecFlower specifications.
    """

    def __init__(
        self,
        image: str | None = None,
        base_image: str | None = None,
        requirements: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.image = image
        self.base_image = base_image
        self.requirements = requirements


class FunctionValidatorFlower(FunctionValidator):
    """
    FunctionValidatorFlower validator.
    """

    image: Optional[str] = None
    base_image: Optional[str] = None
    requirements: Optional[list[str]] = None
