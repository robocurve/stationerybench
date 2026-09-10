"""Register five fixed-setup tasks with binary mean success over 20 trials."""

from __future__ import annotations

import zlib
from collections.abc import Callable

from inspect_robots import Epochs, Scene, Task, episode_length, task

from stationerybench.scoring import task_success
from stationerybench.specs import SPEC_BY_KEY, TaskSpec

K_TRIALS = 20  # published protocol: 20 repetitions per task per model
MAX_SECONDS = 120.0  # 1200 steps at 10 Hz, the published VLA horizon


def make_task(spec: TaskSpec, *, max_seconds: float = MAX_SECONDS) -> Task:
    """Build one fixed scene repeated 20 times, with a configurable time limit."""
    scene = Scene(
        id=spec.key,
        instruction=spec.instruction,
        init_seed=zlib.crc32(spec.key.encode()),
        metadata={
            "benchmark": "stationerybench",
            "task": spec.key,
            "title": spec.title,
            "version": spec.version,
            "bimanual": True,
            "objects": list(spec.objects),
            "setup": list(spec.setup),
            # A str, not a list, on purpose: inspect-robots 0.58 prints
            # scene.metadata["rubric"] above the operator verdict prompt only
            # when it is a non-blank string (session.py prompt_verdict). The
            # operator therefore sees the 0-4 ladder before answering y/n.
            "rubric": "\n".join(f"{i} - {line}" for i, line in enumerate(spec.rubric)),
            "rubric_lines": list(spec.rubric),
            "report_slug": spec.report_slug,
        },
    )
    return Task(
        name=f"stationerybench/{spec.key}",
        scenes=[scene],
        scorer=[task_success(), episode_length()],
        epochs=Epochs(count=K_TRIALS, reducer="mean"),
        max_seconds=max_seconds,
        metadata={"benchmark": "stationerybench", "k_trials": K_TRIALS, "protocol": "fixed-setup"},
    )


@task("stationerybench/uncap_marker")
def uncap_marker(max_seconds: float = MAX_SECONDS) -> Task:
    """Build the registered uncap marker task with the given time limit."""
    return make_task(SPEC_BY_KEY["uncap_marker"], max_seconds=max_seconds)


@task("stationerybench/eraser_from_box")
def eraser_from_box(max_seconds: float = MAX_SECONDS) -> Task:
    """Build the registered eraser from box task with the given time limit."""
    return make_task(SPEC_BY_KEY["eraser_from_box"], max_seconds=max_seconds)


@task("stationerybench/middle_sticky_pad")
def middle_sticky_pad(max_seconds: float = MAX_SECONDS) -> Task:
    """Build the registered middle sticky pad task with the given time limit."""
    return make_task(SPEC_BY_KEY["middle_sticky_pad"], max_seconds=max_seconds)


@task("stationerybench/pour_paperclips")
def pour_paperclips(max_seconds: float = MAX_SECONDS) -> Task:
    """Build the registered pour paperclips task with the given time limit."""
    return make_task(SPEC_BY_KEY["pour_paperclips"], max_seconds=max_seconds)


@task("stationerybench/ruler_handover")
def ruler_handover(max_seconds: float = MAX_SECONDS) -> Task:
    """Build the registered ruler handover task with the given time limit."""
    return make_task(SPEC_BY_KEY["ruler_handover"], max_seconds=max_seconds)


TASK_FACTORIES: dict[str, Callable[..., Task]] = {
    "uncap_marker": uncap_marker,
    "eraser_from_box": eraser_from_box,
    "middle_sticky_pad": middle_sticky_pad,
    "pour_paperclips": pour_paperclips,
    "ruler_handover": ruler_handover,
}
