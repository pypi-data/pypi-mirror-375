# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_python.entities.run._base.entity import RunPythonRun

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_python.entities.run.serve.spec import RunSpecPythonRunServe
    from digitalhub_runtime_python.entities.run.serve.status import RunStatusPythonRunServe


class RunPythonRunServe(RunPythonRun):
    """
    RunPythonRunServe class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecPythonRunServe,
        status: RunStatusPythonRunServe,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecPythonRunServe
        self.status: RunStatusPythonRunServe
