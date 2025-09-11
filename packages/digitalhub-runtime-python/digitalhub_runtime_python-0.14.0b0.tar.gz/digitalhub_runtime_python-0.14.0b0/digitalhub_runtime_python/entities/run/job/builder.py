# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_python.entities._base.runtime_entity.builder import RuntimeEntityBuilderPython
from digitalhub_runtime_python.entities._commons.enums import EntityKinds
from digitalhub_runtime_python.entities.run.job.entity import RunPythonRunJob
from digitalhub_runtime_python.entities.run.job.spec import RunSpecPythonRunJob, RunValidatorPythonRunJob
from digitalhub_runtime_python.entities.run.job.status import RunStatusPythonRunJob


class RunPythonRunJobBuilder(RunBuilder, RuntimeEntityBuilderPython):
    """
    RunPythonRunJobBuilder runner.
    """

    ENTITY_CLASS = RunPythonRunJob
    ENTITY_SPEC_CLASS = RunSpecPythonRunJob
    ENTITY_SPEC_VALIDATOR = RunValidatorPythonRunJob
    ENTITY_STATUS_CLASS = RunStatusPythonRunJob
    ENTITY_KIND = EntityKinds.RUN_PYTHON_JOB.value
