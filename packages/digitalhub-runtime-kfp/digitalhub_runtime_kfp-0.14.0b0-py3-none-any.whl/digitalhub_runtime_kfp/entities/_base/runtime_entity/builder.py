# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
from digitalhub.entities._commons.utils import map_actions

from digitalhub_runtime_kfp.entities._commons.enums import Actions, EntityKinds


class RuntimeEntityBuilderKfp(RuntimeEntityBuilder):
    EXECUTABLE_KIND = EntityKinds.WORKFLOW_KFP.value
    TASKS_KINDS = map_actions(
        [
            (
                EntityKinds.TASK_KFP_PIPELINE.value,
                Actions.PIPELINE.value,
            ),
            (
                EntityKinds.TASK_KFP_BUILD.value,
                Actions.BUILD.value,
            ),
        ]
    )
    RUNS_KINDS = map_actions(
        [
            (
                EntityKinds.RUN_KFP_PIPELINE.value,
                Actions.PIPELINE.value,
            ),
            (
                EntityKinds.RUN_KFP_BUILD.value,
                Actions.BUILD.value,
            ),
        ]
    )
