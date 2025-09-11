# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
from digitalhub.entities._commons.utils import map_actions

from digitalhub_runtime_container.entities._commons.enums import Actions, EntityKinds


class RuntimeEntityBuilderContainer(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.FUNCTION_CONTAINER.value
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_CONTAINER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.TASK_CONTAINER_JOB.value,
                Actions.JOB.value,
            ),
            (
                EntityKinds.TASK_CONTAINER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
            (
                EntityKinds.TASK_CONTAINER_SERVE.value,
                Actions.SERVE.value,
            ),
        ]
    )
    RUN_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_CONTAINER_BUILD.value,
                Actions.BUILD.value,
            ),
            (
                EntityKinds.RUN_CONTAINER_JOB.value,
                Actions.JOB.value,
            ),
            (
                EntityKinds.RUN_CONTAINER_DEPLOY.value,
                Actions.DEPLOY.value,
            ),
            (
                EntityKinds.RUN_CONTAINER_SERVE.value,
                Actions.SERVE.value,
            ),
        ]
    )
