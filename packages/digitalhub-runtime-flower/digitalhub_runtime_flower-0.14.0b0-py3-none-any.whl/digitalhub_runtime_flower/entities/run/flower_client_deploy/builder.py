# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerClient
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.run.flower_client_deploy.entity import RunFlowerClientDeploy
from digitalhub_runtime_flower.entities.run.flower_client_deploy.spec import (
    RunSpecFlowerClientDeploy,
    RunValidatorFlowerClientDeploy,
)
from digitalhub_runtime_flower.entities.run.flower_client_deploy.status import RunStatusFlowerClientDeploy


class RunFlowerClientDeployBuilder(RunBuilder, RuntimeEntityBuilderFlowerClient):
    """
    RunFlowerClientDeploy builder.
    """

    ENTITY_CLASS = RunFlowerClientDeploy
    ENTITY_SPEC_CLASS = RunSpecFlowerClientDeploy
    ENTITY_SPEC_VALIDATOR = RunValidatorFlowerClientDeploy
    ENTITY_STATUS_CLASS = RunStatusFlowerClientDeploy
    ENTITY_KIND = EntityKinds.RUN_FLOWER_CLIENT_DEPLOY.value
