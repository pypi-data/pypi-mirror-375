# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from digitalhub_runtime_kfp.entities._commons.enums import EntityKinds
from digitalhub_runtime_kfp.entities.run.build.builder import RunKfpRunBuildBuilder
from digitalhub_runtime_kfp.entities.run.pipeline.builder import RunKfpRunPipelineBuilder
from digitalhub_runtime_kfp.entities.task.build.builder import TaskKfpBuildBuilder
from digitalhub_runtime_kfp.entities.task.pipeline.builder import TaskKfpPipelineBuilder
from digitalhub_runtime_kfp.entities.workflow.kfp.builder import WorkflowKfpBuilder

entity_builders = (
    (EntityKinds.WORKFLOW_KFP.value, WorkflowKfpBuilder),
    (EntityKinds.TASK_KFP_PIPELINE.value, TaskKfpPipelineBuilder),
    (EntityKinds.TASK_KFP_BUILD.value, TaskKfpBuildBuilder),
    (EntityKinds.RUN_KFP_BUILD.value, RunKfpRunBuildBuilder),
    (EntityKinds.RUN_KFP_PIPELINE.value, RunKfpRunPipelineBuilder),
)

try:
    from digitalhub_runtime_kfp.runtimes.builder import RuntimeKfpBuilder

    runtime_builders = ((kind, RuntimeKfpBuilder) for kind in [e.value for e in EntityKinds])
except ImportError:
    runtime_builders = tuple()
