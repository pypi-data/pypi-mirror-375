# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_container.entities._base.runtime_entity.builder import RuntimeEntityBuilderContainer
from digitalhub_runtime_container.entities._commons.enums import EntityKinds
from digitalhub_runtime_container.entities.run.serve.entity import RunContainerRunServe
from digitalhub_runtime_container.entities.run.serve.spec import RunSpecContainerRunServe, RunValidatorContainerRunServe
from digitalhub_runtime_container.entities.run.serve.status import RunStatusContainerRunServe


class RunContainerRunServeBuilder(RunBuilder, RuntimeEntityBuilderContainer):
    """
    RunContainerRunServeBuilder runner.
    """

    ENTITY_CLASS = RunContainerRunServe
    ENTITY_SPEC_CLASS = RunSpecContainerRunServe
    ENTITY_SPEC_VALIDATOR = RunValidatorContainerRunServe
    ENTITY_STATUS_CLASS = RunStatusContainerRunServe
    ENTITY_KIND = EntityKinds.RUN_CONTAINER_SERVE.value
