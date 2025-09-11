# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from enum import Enum


class EntityKinds(Enum):
    """
    Entity kinds.
    """

    FUNCTION_FLOWER_APP = "flower-app"
    TASK_FLOWER_APP_TRAIN = "flower-app+train"
    RUN_FLOWER_APP_TRAIN = "flower-app+train:run"

    FUNCTION_FLOWER_SERVER = "flower-server"
    TASK_FLOWER_SERVER_BUILD = "flower-server+build"
    RUN_FLOWER_SERVER_BUILD = "flower-server+build:run"
    TASK_FLOWER_SERVER_DEPLOY = "flower-server+deploy"
    RUN_FLOWER_SERVER_DEPLOY = "flower-server+deploy:run"

    FUNCTION_FLOWER_CLIENT = "flower-client"
    TASK_FLOWER_CLIENT_BUILD = "flower-client+build"
    RUN_FLOWER_CLIENT_BUILD = "flower-client+build:run"
    TASK_FLOWER_CLIENT_DEPLOY = "flower-client+deploy"
    RUN_FLOWER_CLIENT_DEPLOY = "flower-client+deploy:run"


class Actions(Enum):
    """
    Task actions.
    """

    BUILD = "build"
    DEPLOY = "deploy"
    TRAIN = "train"
