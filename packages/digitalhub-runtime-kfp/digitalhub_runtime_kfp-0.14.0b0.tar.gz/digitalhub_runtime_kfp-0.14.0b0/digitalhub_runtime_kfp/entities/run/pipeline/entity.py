# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_kfp.entities.run._base.entity import RunKfpRun

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_kfp.entities.run.pipeline.spec import RunSpecKfpRunPipeline
    from digitalhub_runtime_kfp.entities.run.pipeline.status import RunStatusKfpRunPipeline


class RunKfpRunPipeline(RunKfpRun):
    """
    RunKfpRunPipeline class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecKfpRunPipeline,
        status: RunStatusKfpRunPipeline,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecKfpRunPipeline
        self.status: RunStatusKfpRunPipeline
