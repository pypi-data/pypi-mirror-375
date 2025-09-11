# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub_runtime_kfp.entities.run._base.spec import RunSpecKfpRun, RunValidatorKfpRun


class RunSpecKfpRunPipeline(RunSpecKfpRun):
    """RunSpecKfpRunPipeline specifications."""


class RunValidatorKfpRunPipeline(RunValidatorKfpRun):
    """RunValidatorKfpRunPipeline validator."""
