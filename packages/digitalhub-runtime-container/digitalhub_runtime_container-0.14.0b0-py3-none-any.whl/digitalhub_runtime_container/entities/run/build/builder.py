# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_container.entities._base.runtime_entity.builder import RuntimeEntityBuilderContainer
from digitalhub_runtime_container.entities._commons.enums import EntityKinds
from digitalhub_runtime_container.entities.run.build.entity import RunContainerRunBuild
from digitalhub_runtime_container.entities.run.build.spec import RunSpecContainerRunBuild, RunValidatorContainerRunBuild
from digitalhub_runtime_container.entities.run.build.status import RunStatusContainerRunBuild


class RunContainerRunBuildBuilder(RunBuilder, RuntimeEntityBuilderContainer):
    """
    RunContainerRunBuildBuilder runner.
    """

    ENTITY_CLASS = RunContainerRunBuild
    ENTITY_SPEC_CLASS = RunSpecContainerRunBuild
    ENTITY_SPEC_VALIDATOR = RunValidatorContainerRunBuild
    ENTITY_STATUS_CLASS = RunStatusContainerRunBuild
    ENTITY_KIND = EntityKinds.RUN_CONTAINER_BUILD.value
