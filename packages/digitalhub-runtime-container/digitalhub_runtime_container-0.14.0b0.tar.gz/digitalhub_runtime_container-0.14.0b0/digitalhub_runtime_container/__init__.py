# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_container.entities._commons.enums import EntityKinds
from digitalhub_runtime_container.entities.function.container.builder import FunctionContainerBuilder
from digitalhub_runtime_container.entities.run.build.builder import RunContainerRunBuildBuilder
from digitalhub_runtime_container.entities.run.deploy.builder import RunContainerRunDeployBuilder
from digitalhub_runtime_container.entities.run.job.builder import RunContainerRunJobBuilder
from digitalhub_runtime_container.entities.run.serve.builder import RunContainerRunServeBuilder
from digitalhub_runtime_container.entities.task.build.builder import TaskContainerBuildBuilder
from digitalhub_runtime_container.entities.task.deploy.builder import TaskContainerDeployBuilder
from digitalhub_runtime_container.entities.task.job.builder import TaskContainerJobBuilder
from digitalhub_runtime_container.entities.task.serve.builder import TaskContainerServeBuilder

entity_builders = (
    (EntityKinds.FUNCTION_CONTAINER.value, FunctionContainerBuilder),
    (EntityKinds.TASK_CONTAINER_BUILD.value, TaskContainerBuildBuilder),
    (EntityKinds.TASK_CONTAINER_DEPLOY.value, TaskContainerDeployBuilder),
    (EntityKinds.TASK_CONTAINER_JOB.value, TaskContainerJobBuilder),
    (EntityKinds.TASK_CONTAINER_SERVE.value, TaskContainerServeBuilder),
    (EntityKinds.RUN_CONTAINER_BUILD.value, RunContainerRunBuildBuilder),
    (EntityKinds.RUN_CONTAINER_DEPLOY.value, RunContainerRunDeployBuilder),
    (EntityKinds.RUN_CONTAINER_JOB.value, RunContainerRunJobBuilder),
    (EntityKinds.RUN_CONTAINER_SERVE.value, RunContainerRunServeBuilder),
)

try:
    from digitalhub_runtime_container.runtimes.builder import RuntimeContainerBuilder

    runtime_builders = ((kind, RuntimeContainerBuilder) for kind in [e.value for e in EntityKinds])
except ImportError:
    runtime_builders = tuple()
