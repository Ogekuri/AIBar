"""
@file
@brief Hatchling build hook that keeps non-indispensable VCS files out of the sdist.
@details Hatchling unconditionally force-includes the repository `.gitignore`
into every sdist (`hatchling.builders.sdist.SdistBuilder.get_default_build_data`),
independent of `[tool.hatch.build.targets.sdist]` include and exclude settings.
This hook removes that force-include entry for the sdist target only, so the sdist
carries exclusively the runtime package, release metadata, and this hook. Wheel
builds are not affected, and the wheel never contained `.gitignore`.
@satisfies PRJ-010
@satisfies TST-037
"""

from __future__ import annotations

import os
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# var EXCLUDED_SDIST_BASENAMES {frozenset[str]} Basenames force-included by hatchling that the sdist must not carry.
EXCLUDED_SDIST_BASENAMES = frozenset({".gitignore"})


class CustomBuildHook(BuildHookInterface):
    """
    @brief Hatchling build hook removing excluded basenames from the sdist force-include map.
    @details Registered through `[tool.hatch.build.hooks.custom]` in `pyproject.toml`.
    Hatchling discovers the class via `PLUGIN_NAME` and invokes `initialize` once per build target.
    @satisfies TST-037
    """

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """
        @brief Drop excluded basenames from `build_data["force_include"]` for sdist builds only.
        @details Iterates a snapshot of the force-include keys so deletion during iteration is safe.
        Non-sdist targets return without mutation. Complexity O(F) over force-include entries F; space O(1).
        @param version {str} Build version supplied by hatchling (unused).
        @param build_data {dict[str, Any]} Mutable hatchling build data carrying `force_include` mapping of absolute source path to archive path.
        @return {None} Function return value.
        @satisfies PRJ-010
        """
        del version
        if self.target_name != "sdist":
            return
        force_include: dict[str, str] = build_data.get("force_include", {})
        for source_path in list(force_include):
            if os.path.basename(source_path) in EXCLUDED_SDIST_BASENAMES:
                del force_include[source_path]
