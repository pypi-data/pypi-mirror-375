# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_python.entities._base.runtime_entity.builder import RuntimeEntityBuilderPython
from digitalhub_runtime_python.entities._commons.enums import EntityKinds
from digitalhub_runtime_python.entities.run.serve.entity import RunPythonRunServe
from digitalhub_runtime_python.entities.run.serve.spec import RunSpecPythonRunServe, RunValidatorPythonRunServe
from digitalhub_runtime_python.entities.run.serve.status import RunStatusPythonRunServe


class RunPythonRunServeBuilder(RunBuilder, RuntimeEntityBuilderPython):
    """
    RunPythonRunServeBuilder runner.
    """

    ENTITY_CLASS = RunPythonRunServe
    ENTITY_SPEC_CLASS = RunSpecPythonRunServe
    ENTITY_SPEC_VALIDATOR = RunValidatorPythonRunServe
    ENTITY_STATUS_CLASS = RunStatusPythonRunServe
    ENTITY_KIND = EntityKinds.RUN_PYTHON_SERVE.value
