# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from pathlib import Path


def run_simulation(root: Path, run_args: str) -> None:
    """
    Run a local simulation.

    Parameters
    ----------
    root : Path
        The root directory of the project.
    run_args : str | None
        The run arguments.

    Returns
    -------
    None
    """
    current_dir = os.getcwd()
    os.chdir(root)
    os.system(f"flwr run {run_args}")
    os.chdir(current_dir)
