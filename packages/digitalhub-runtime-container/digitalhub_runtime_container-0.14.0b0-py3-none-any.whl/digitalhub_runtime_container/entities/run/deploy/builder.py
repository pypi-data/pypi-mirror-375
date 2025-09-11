# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_container.entities._base.runtime_entity.builder import RuntimeEntityBuilderContainer
from digitalhub_runtime_container.entities._commons.enums import EntityKinds
from digitalhub_runtime_container.entities.run.deploy.entity import RunContainerRunDeploy
from digitalhub_runtime_container.entities.run.deploy.spec import (
    RunSpecContainerRunDeploy,
    RunValidatorContainerRunDeploy,
)
from digitalhub_runtime_container.entities.run.deploy.status import RunStatusContainerRunDeploy


class RunContainerRunDeployBuilder(RunBuilder, RuntimeEntityBuilderContainer):
    """
    RunContainerRunDeployBuilder runner.
    """

    ENTITY_CLASS = RunContainerRunDeploy
    ENTITY_SPEC_CLASS = RunSpecContainerRunDeploy
    ENTITY_SPEC_VALIDATOR = RunValidatorContainerRunDeploy
    ENTITY_STATUS_CLASS = RunStatusContainerRunDeploy
    ENTITY_KIND = EntityKinds.RUN_CONTAINER_DEPLOY.value
