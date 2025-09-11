# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_kfp.entities._base.runtime_entity.builder import RuntimeEntityBuilderKfp
from digitalhub_runtime_kfp.entities._commons.enums import EntityKinds
from digitalhub_runtime_kfp.entities.run.build.entity import RunKfpRunBuild
from digitalhub_runtime_kfp.entities.run.build.spec import RunSpecKfpRunBuild, RunValidatorKfpRunBuild
from digitalhub_runtime_kfp.entities.run.build.status import RunStatusKfpRunBuild


class RunKfpRunBuildBuilder(RunBuilder, RuntimeEntityBuilderKfp):
    """
    RunKfpRunBuildBuilder runer.
    """

    ENTITY_CLASS = RunKfpRunBuild
    ENTITY_SPEC_CLASS = RunSpecKfpRunBuild
    ENTITY_SPEC_VALIDATOR = RunValidatorKfpRunBuild
    ENTITY_STATUS_CLASS = RunStatusKfpRunBuild
    ENTITY_KIND = EntityKinds.RUN_KFP_BUILD.value
