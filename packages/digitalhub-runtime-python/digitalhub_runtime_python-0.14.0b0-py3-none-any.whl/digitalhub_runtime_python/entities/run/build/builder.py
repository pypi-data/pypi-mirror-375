# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_python.entities._base.runtime_entity.builder import RuntimeEntityBuilderPython
from digitalhub_runtime_python.entities._commons.enums import EntityKinds
from digitalhub_runtime_python.entities.run.build.entity import RunPythonRunBuild
from digitalhub_runtime_python.entities.run.build.spec import RunSpecPythonRunBuild, RunValidatorPythonRunBuild
from digitalhub_runtime_python.entities.run.build.status import RunStatusPythonRunBuild


class RunPythonRunBuildBuilder(RunBuilder, RuntimeEntityBuilderPython):
    """
    RunPythonRunBuildBuilder runner.
    """

    ENTITY_CLASS = RunPythonRunBuild
    ENTITY_SPEC_CLASS = RunSpecPythonRunBuild
    ENTITY_SPEC_VALIDATOR = RunValidatorPythonRunBuild
    ENTITY_STATUS_CLASS = RunStatusPythonRunBuild
    ENTITY_KIND = EntityKinds.RUN_PYTHON_BUILD.value
