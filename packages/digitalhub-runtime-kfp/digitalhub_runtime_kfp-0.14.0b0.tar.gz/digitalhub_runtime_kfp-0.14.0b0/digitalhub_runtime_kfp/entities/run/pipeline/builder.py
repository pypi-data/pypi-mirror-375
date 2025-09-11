# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_kfp.entities._base.runtime_entity.builder import RuntimeEntityBuilderKfp
from digitalhub_runtime_kfp.entities._commons.enums import EntityKinds
from digitalhub_runtime_kfp.entities.run.pipeline.entity import RunKfpRunPipeline
from digitalhub_runtime_kfp.entities.run.pipeline.spec import RunSpecKfpRunPipeline, RunValidatorKfpRunPipeline
from digitalhub_runtime_kfp.entities.run.pipeline.status import RunStatusKfpRunPipeline


class RunKfpRunPipelineBuilder(RunBuilder, RuntimeEntityBuilderKfp):
    """
    RunKfpRunPipelineBuilder runer.
    """

    ENTITY_CLASS = RunKfpRunPipeline
    ENTITY_SPEC_CLASS = RunSpecKfpRunPipeline
    ENTITY_SPEC_VALIDATOR = RunValidatorKfpRunPipeline
    ENTITY_STATUS_CLASS = RunStatusKfpRunPipeline
    ENTITY_KIND = EntityKinds.RUN_KFP_PIPELINE.value
