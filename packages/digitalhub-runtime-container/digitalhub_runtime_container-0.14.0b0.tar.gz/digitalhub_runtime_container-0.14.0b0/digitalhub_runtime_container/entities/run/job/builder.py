# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_container.entities._base.runtime_entity.builder import RuntimeEntityBuilderContainer
from digitalhub_runtime_container.entities._commons.enums import EntityKinds
from digitalhub_runtime_container.entities.run.job.entity import RunContainerRunJob
from digitalhub_runtime_container.entities.run.job.spec import RunSpecContainerRunJob, RunValidatorContainerRunJob
from digitalhub_runtime_container.entities.run.job.status import RunStatusContainerRunJob


class RunContainerRunJobBuilder(RunBuilder, RuntimeEntityBuilderContainer):
    """
    RunContainerRunJobBuilder runner.
    """

    ENTITY_CLASS = RunContainerRunJob
    ENTITY_SPEC_CLASS = RunSpecContainerRunJob
    ENTITY_SPEC_VALIDATOR = RunValidatorContainerRunJob
    ENTITY_STATUS_CLASS = RunStatusContainerRunJob
    ENTITY_KIND = EntityKinds.RUN_CONTAINER_JOB.value
