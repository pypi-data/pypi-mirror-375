# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
from digitalhub.entities._commons.utils import map_actions

from digitalhub_runtime_flower.entities._commons.enums import Actions, EntityKinds


class RuntimeEntityBuilderFlower(RuntimeEntityBuilder):
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_FLOWER_APP_TRAIN.value,
                Actions.TRAIN.value,
            ),
            (
                EntityKinds.TASK_FLOWER_SERVER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.TASK_FLOWER_SERVER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
            (
                EntityKinds.TASK_FLOWER_CLIENT_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.TASK_FLOWER_CLIENT_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )
    RUN_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_FLOWER_APP_TRAIN.value,
                Actions.TRAIN.value,
            ),
            (
                EntityKinds.RUN_FLOWER_SERVER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.RUN_FLOWER_SERVER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
            (
                EntityKinds.RUN_FLOWER_CLIENT_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.RUN_FLOWER_CLIENT_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )


class RuntimeEntityBuilderFlowerApp(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.FUNCTION_FLOWER_APP.value
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_FLOWER_APP_TRAIN.value,
                Actions.TRAIN.value,
            ),
        ]
    )
    RUN_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_FLOWER_APP_TRAIN.value,
                Actions.TRAIN.value,
            ),
        ]
    )


class RuntimeEntityBuilderFlowerServer(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.FUNCTION_FLOWER_SERVER.value
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_FLOWER_SERVER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.TASK_FLOWER_SERVER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )
    RUN_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_FLOWER_SERVER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.RUN_FLOWER_SERVER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )


class RuntimeEntityBuilderFlowerClient(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.FUNCTION_FLOWER_CLIENT.value
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_FLOWER_CLIENT_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.TASK_FLOWER_CLIENT_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )
    RUN_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_FLOWER_CLIENT_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.RUN_FLOWER_CLIENT_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
        ]
    )
