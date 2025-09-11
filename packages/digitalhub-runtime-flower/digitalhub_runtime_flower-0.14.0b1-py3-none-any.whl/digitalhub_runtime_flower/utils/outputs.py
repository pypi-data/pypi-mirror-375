# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._commons.enums import State
from digitalhub.utils.logger import LOGGER


def build_status(output: str) -> dict:
    """
    Build status of the executed run.

    Parameters
    ----------
    output : str
        The output of the flower simulation.

    Returns
    -------
    dict
        Status of the executed run.
    """
    try:
        return {
            "state": State.COMPLETED.value,
            "output": output,
        }
    except Exception as e:
        msg = f"Something got wrong during status creation. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e
