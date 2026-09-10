"""Two-epoch mock evaluations reduce binary success without filesystem logs."""

from dataclasses import replace
from unittest.mock import patch

import pytest
from inspect_robots import Epochs, TrialRecord
from inspect_robots import eval as rl_eval

from stationerybench import (
    SPECS,
    NoopStationeryPolicy,
    RandomStationeryPolicy,
    ScriptedStationeryPolicy,
    StationeryEmbodiment,
    TaskSpec,
    make_task,
    task_success,
)


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.key)
@pytest.mark.parametrize(
    ("policy_class", "expected"),
    [(ScriptedStationeryPolicy, 1.0), (NoopStationeryPolicy, 0.0)],
)
def test_eval_two_epochs(spec: TaskSpec, policy_class: type, expected: float) -> None:
    task = replace(make_task(spec), epochs=Epochs(count=2, reducer="mean"))
    embodiment = StationeryEmbodiment()
    try:
        # eval's provenance probe invokes git even with sinks disabled. Suppress
        # only that probe; run the actual rollout, scoring, and reduction.
        with patch("inspect_robots.eval._git_commit", return_value=None):
            (log,) = rl_eval(task, policy_class(), embodiment, sinks=[], store_actions=False)
    finally:
        embodiment.close()
    assert log.status == "success"
    assert log.results.total_trials == 2
    assert log.results.metrics["task_success"] == expected
    (sample,) = log.samples
    assert len(sample.epochs) == 2
    assert sample.reduced["task_success"] == expected
    assert sample.instruction == spec.instruction
    assert all(epoch["task_success"] == bool(expected) for epoch in sample.epochs)
    assert sample.reduced["episode_length"] == (4.0 if expected else 1200.0)


def test_random_baseline_fails_for_fixed_seed() -> None:
    task = replace(make_task(SPECS[0]), epochs=Epochs(count=2, reducer="mean"))
    embodiment = StationeryEmbodiment()
    try:
        with patch("inspect_robots.eval._git_commit", return_value=None):
            (log,) = rl_eval(
                task, RandomStationeryPolicy(), embodiment, sinks=[], store_actions=False
            )
    finally:
        embodiment.close()
    assert log.status == "success"
    assert log.samples[0].reduced["task_success"] == 0.0


@pytest.mark.parametrize(
    ("termination", "verdict", "expected"),
    [
        ("success", None, True),
        ("success", "n", True),
        (None, "y", True),
        (None, " YES ", True),
        (None, "partial", False),
        (None, "n", False),
        (None, None, False),
    ],
)
def test_task_success_signals(termination: str | None, verdict: str | None, expected: bool) -> None:
    record = TrialRecord(
        scene_id="unit",
        epoch=0,
        seed=0,
        termination_reason=termination,
        operator_judgement=verdict,
    )
    scorer = task_success()
    assert scorer.name == "task_success"
    score = scorer(record, None)
    assert score.value is expected
    assert score.explanation
