"""Mock declarations and deterministic action behavior satisfy the adapter contract."""

import numpy as np
from inspect_robots import Action, Scene
from inspect_robots.conformance import assert_embodiment_conformant
from inspect_robots.embodiment import PRIVILEGED_SUCCESS, RENDERABLE, SEEDABLE

from stationerybench import (
    SPECS,
    NoopStationeryPolicy,
    RandomStationeryPolicy,
    ScriptedStationeryPolicy,
    StationeryEmbodiment,
    make_task,
)


def test_stationery_embodiment_is_conformant() -> None:
    embodiment = StationeryEmbodiment()
    try:
        assert_embodiment_conformant(embodiment.info)
        assert embodiment.info.capabilities == frozenset({SEEDABLE, RENDERABLE, PRIVILEGED_SUCCESS})
    finally:
        embodiment.close()


def test_reset_is_seeded_and_preserves_instruction() -> None:
    embodiment = StationeryEmbodiment()
    scene = make_task(SPECS[0]).scenes[0]
    first = embodiment.reset(scene)
    repeated = embodiment.reset(scene, seed=0)
    np.testing.assert_array_equal(first.state["goal_dir"], repeated.state["goal_dir"])
    different = embodiment.reset(scene, seed=1)
    assert not np.array_equal(first.state["goal_dir"], different.state["goal_dir"])
    assert different.instruction == scene.instruction
    assert embodiment.num_steps == 0
    result = embodiment.step(Action(data=np.zeros(8)))
    assert result.observation.instruction == scene.instruction
    assert result.reward == -1.0
    assert not result.terminated and not result.truncated
    assert result.termination_reason is None
    assert result.info == {"success": False, "progress": 0.0}
    assert embodiment.reset(Scene(id="bare", instruction="Unchanged.")).instruction == "Unchanged."
    embodiment.close()


def test_progress_requires_alignment_and_resets() -> None:
    embodiment = StationeryEmbodiment(step_size=0.75)
    scene = make_task(SPECS[0]).scenes[0]
    observation = embodiment.reset(scene, seed=42)
    goal = observation.state["goal_dir"]
    opposed = embodiment.step(Action(data=np.concatenate([-goal, [3.0, -3.0]])))
    assert opposed.info["progress"] == 0.0
    policy = ScriptedStationeryPolicy(chunk_size=2)
    policy.reset(scene)
    chunk = policy.act(observation)
    assert policy.num_inferences == 1
    first, second = [embodiment.step(action) for action in chunk.actions]
    assert first.info["progress"] == 0.75
    assert not first.terminated
    assert second.info["progress"] == 1.0
    assert second.terminated and second.termination_reason == "success"
    assert second.reward == 0.0
    np.testing.assert_array_equal(second.observation.state["left_eef"], goal[:3])
    np.testing.assert_array_equal(second.observation.state["right_eef"], goal[3:])
    image = second.observation.images["overhead"]
    assert image.shape == (24, 24, 3)
    assert image.dtype == np.uint8
    assert np.all(image[:, :, 1] == 200)
    reset = embodiment.reset(scene, seed=42)
    assert embodiment.num_steps == 0
    assert reset.state["progress"].item() == 0.0
    assert not np.any(reset.images["overhead"])
    policy.reset(scene)
    assert policy.num_inferences == 0
    embodiment.close()


def test_random_policy_reproducible_streams_and_chunks() -> None:
    scene = make_task(SPECS[0]).scenes[0]
    embodiment = StationeryEmbodiment()
    observation = embodiment.reset(scene)
    first = RandomStationeryPolicy(chunk_size=3, seed=7)
    second = RandomStationeryPolicy(chunk_size=3, seed=7)
    previous = None
    for _ in range(2):
        first.reset(scene)
        second.reset(scene)
        assert first.num_inferences == second.num_inferences == 0
        a = first.act(observation)
        b = second.act(observation)
        assert first.num_inferences == second.num_inferences == 1
        assert len(a.actions) == len(b.actions) == 3
        for left, right in zip(a.actions, b.actions, strict=True):
            np.testing.assert_array_equal(left.data, right.data)
            assert np.all(np.abs(left.data) <= 1.0)
        if previous is not None:
            assert not np.array_equal(previous, a.actions[0].data)
        previous = a.actions[0].data.copy()
    embodiment.close()


def test_noop_policy_horizon_and_accounting() -> None:
    scene = make_task(SPECS[0]).scenes[0]
    embodiment = StationeryEmbodiment()
    observation = embodiment.reset(scene)
    policy = NoopStationeryPolicy(chunk_size=3)
    policy.reset(scene)
    assert policy.num_inferences == 0
    chunk = policy.act(observation)
    assert policy.num_inferences == 1
    assert len(chunk.actions) == policy.config.action_horizon == 3
    for action in chunk.actions:
        np.testing.assert_array_equal(action.data, np.zeros(8))
    policy.reset(scene)
    assert policy.num_inferences == 0
    embodiment.close()
