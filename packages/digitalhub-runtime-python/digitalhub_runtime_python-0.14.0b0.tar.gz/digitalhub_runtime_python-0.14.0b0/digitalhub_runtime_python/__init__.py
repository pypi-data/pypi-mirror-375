# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_python.entities._commons.enums import EntityKinds
from digitalhub_runtime_python.entities.function.python.builder import FunctionPythonBuilder
from digitalhub_runtime_python.entities.run.build.builder import RunPythonRunBuildBuilder
from digitalhub_runtime_python.entities.run.job.builder import RunPythonRunJobBuilder
from digitalhub_runtime_python.entities.run.serve.builder import RunPythonRunServeBuilder
from digitalhub_runtime_python.entities.task.build.builder import TaskPythonBuildBuilder
from digitalhub_runtime_python.entities.task.job.builder import TaskPythonJobBuilder
from digitalhub_runtime_python.entities.task.serve.builder import TaskPythonServeBuilder
from digitalhub_runtime_python.utils.utils import handler

entity_builders = (
    (EntityKinds.FUNCTION_PYTHON.value, FunctionPythonBuilder),
    (EntityKinds.TASK_PYTHON_BUILD.value, TaskPythonBuildBuilder),
    (EntityKinds.TASK_PYTHON_JOB.value, TaskPythonJobBuilder),
    (EntityKinds.TASK_PYTHON_SERVE.value, TaskPythonServeBuilder),
    (EntityKinds.RUN_PYTHON_BUILD.value, RunPythonRunBuildBuilder),
    (EntityKinds.RUN_PYTHON_JOB.value, RunPythonRunJobBuilder),
    (EntityKinds.RUN_PYTHON_SERVE.value, RunPythonRunServeBuilder),
)

try:
    from digitalhub_runtime_python.runtimes.builder import RuntimePythonBuilder

    runtime_builders = ((kind, RuntimePythonBuilder) for kind in [e.value for e in EntityKinds])
except ImportError:
    runtime_builders = tuple()
