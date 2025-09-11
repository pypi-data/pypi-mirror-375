# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.function.flower_app.builder import FunctionFlowerAppBuilder
from digitalhub_runtime_flower.entities.function.flower_client.builder import FunctionFlowerClientBuilder
from digitalhub_runtime_flower.entities.function.flower_server.builder import FunctionFlowerServerBuilder
from digitalhub_runtime_flower.entities.run.flower_app_train.builder import RunFlowerAppTrainBuilder
from digitalhub_runtime_flower.entities.run.flower_client_build.builder import RunFlowerClientBuildBuilder
from digitalhub_runtime_flower.entities.run.flower_client_deploy.builder import RunFlowerClientDeployBuilder
from digitalhub_runtime_flower.entities.run.flower_server_build.builder import RunFlowerServerBuildBuilder
from digitalhub_runtime_flower.entities.run.flower_server_deploy.builder import RunFlowerServerDeployBuilder
from digitalhub_runtime_flower.entities.task.flower_app_train.builder import TaskFlowerAppTrainBuilder
from digitalhub_runtime_flower.entities.task.flower_client_build.builder import TaskFlowerClientBuildBuilder
from digitalhub_runtime_flower.entities.task.flower_client_deploy.builder import TaskFlowerClientDeployBuilder
from digitalhub_runtime_flower.entities.task.flower_server_build.builder import TaskFlowerServerBuildBuilder
from digitalhub_runtime_flower.entities.task.flower_server_deploy.builder import TaskFlowerServerDeployBuilder

entity_builders = (
    (EntityKinds.FUNCTION_FLOWER_APP.value, FunctionFlowerAppBuilder),
    (EntityKinds.FUNCTION_FLOWER_SERVER.value, FunctionFlowerServerBuilder),
    (EntityKinds.FUNCTION_FLOWER_CLIENT.value, FunctionFlowerClientBuilder),
    (EntityKinds.TASK_FLOWER_APP_TRAIN.value, TaskFlowerAppTrainBuilder),
    (EntityKinds.TASK_FLOWER_SERVER_BUILD.value, TaskFlowerServerBuildBuilder),
    (EntityKinds.TASK_FLOWER_SERVER_DEPLOY.value, TaskFlowerServerDeployBuilder),
    (EntityKinds.TASK_FLOWER_CLIENT_BUILD.value, TaskFlowerClientBuildBuilder),
    (EntityKinds.TASK_FLOWER_CLIENT_DEPLOY.value, TaskFlowerClientDeployBuilder),
    (EntityKinds.RUN_FLOWER_APP_TRAIN.value, RunFlowerAppTrainBuilder),
    (EntityKinds.RUN_FLOWER_SERVER_BUILD.value, RunFlowerServerBuildBuilder),
    (EntityKinds.RUN_FLOWER_SERVER_DEPLOY.value, RunFlowerServerDeployBuilder),
    (EntityKinds.RUN_FLOWER_CLIENT_BUILD.value, RunFlowerClientBuildBuilder),
    (EntityKinds.RUN_FLOWER_CLIENT_DEPLOY.value, RunFlowerClientDeployBuilder),
)

try:
    from digitalhub_runtime_flower.runtimes.builder import RuntimeFlowerAppBuilder, RuntimeFlowerBuilder

    runtime_builders = tuple(
        (
            e.value,
            RuntimeFlowerAppBuilder
            if e
            in (
                EntityKinds.FUNCTION_FLOWER_APP,
                EntityKinds.TASK_FLOWER_APP_TRAIN,
                EntityKinds.RUN_FLOWER_APP_TRAIN,
            )
            else RuntimeFlowerBuilder,
        )
        for e in EntityKinds
    )


except ImportError:
    runtime_builders = tuple()
