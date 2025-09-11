# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_container.entities.run._base.entity import RunContainerRun

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_container.entities.run.job.spec import RunSpecContainerRunJob
    from digitalhub_runtime_container.entities.run.job.status import RunStatusContainerRunJob


class RunContainerRunJob(RunContainerRun):
    """
    RunContainerRunJob class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecContainerRunJob,
        status: RunStatusContainerRunJob,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecContainerRunJob
        self.status: RunStatusContainerRunJob
