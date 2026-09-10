"""StationeryBench: five fixed bimanual tasks and mock evaluation components.

Importing registers the five task factories. Installed entry points make tasks,
policies, and the embodiment discoverable by Inspect Robots without an import.
"""

from __future__ import annotations

from stationerybench.embodiment import StationeryEmbodiment
from stationerybench.policies import (
    NoopStationeryPolicy,
    RandomStationeryPolicy,
    ScriptedStationeryPolicy,
)
from stationerybench.scoring import task_success
from stationerybench.specs import RUBRIC_PRINCIPLES, SPEC_BY_KEY, SPECS, TaskSpec
from stationerybench.tasks import (
    K_TRIALS,
    MAX_SECONDS,
    TASK_FACTORIES,
    eraser_from_box,
    make_task,
    middle_sticky_pad,
    pour_paperclips,
    ruler_handover,
    uncap_marker,
)

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("stationerybench")
except PackageNotFoundError:  # pragma: no cover - only hit in a non-installed tree
    __version__ = "0.0.0+unknown"

__all__ = [
    "K_TRIALS",
    "MAX_SECONDS",
    "RUBRIC_PRINCIPLES",
    "SPECS",
    "SPEC_BY_KEY",
    "TASK_FACTORIES",
    "NoopStationeryPolicy",
    "RandomStationeryPolicy",
    "ScriptedStationeryPolicy",
    "StationeryEmbodiment",
    "TaskSpec",
    "__version__",
    "eraser_from_box",
    "make_task",
    "middle_sticky_pad",
    "pour_paperclips",
    "ruler_handover",
    "task_success",
    "uncap_marker",
]
