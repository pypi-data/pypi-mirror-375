# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class FABSource(BaseModel):
    """
    FABModel for Flower Application Bundle.
    """

    source: Optional[str] = None
    """Git source."""

    clientapp: Optional[str] = None
    """ClientApp source."""

    serverapp: Optional[str] = None
    """ServerApp source."""

    clientbase64: Optional[str] = None
    """ClientBase64 source."""

    serverbase64: Optional[str] = None
    """ServerBase64 source."""
