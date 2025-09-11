# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub_runtime_kfp.entities.run._base.entity import RunKfpRun

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

    from digitalhub_runtime_kfp.entities.run.build.spec import RunSpecKfpRunBuild
    from digitalhub_runtime_kfp.entities.run.build.status import RunStatusKfpRunBuild


class RunKfpRunBuild(RunKfpRun):
    """
    RunKfpRunBuild class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: RunSpecKfpRunBuild,
        status: RunStatusKfpRunBuild,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: RunSpecKfpRunBuild
        self.status: RunStatusKfpRunBuild
