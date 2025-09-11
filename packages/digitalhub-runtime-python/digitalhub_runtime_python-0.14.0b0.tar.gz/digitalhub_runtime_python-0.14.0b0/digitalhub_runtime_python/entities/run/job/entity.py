# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_python.entities.run._base.entity import RunPythonRun

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_python.entities.run.job.spec import RunSpecPythonRunJob
    from digitalhub_runtime_python.entities.run.job.status import RunStatusPythonRunJob


class RunPythonRunJob(RunPythonRun):
    """
    RunPythonRunJob class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecPythonRunJob,
        status: RunStatusPythonRunJob,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecPythonRunJob
        self.status: RunStatusPythonRunJob
