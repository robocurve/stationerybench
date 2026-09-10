"""Factories, installed entry-point declarations, and scene metadata agree."""

import json
import zlib
from importlib import import_module
from pathlib import Path

import pytest
from inspect_robots import Epochs, Task
from inspect_robots.registry import registered, resolve

from stationerybench import K_TRIALS, MAX_SECONDS, SPECS, TASK_FACTORIES, TaskSpec, make_task

ROOT = Path(__file__).resolve().parents[1]


def test_factory_and_entry_point_names() -> None:
    # All CI test jobs use Python 3.11+, where tomllib is in the standard library.
    tomllib = pytest.importorskip("tomllib")
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    entries = project["entry-points"]["inspect_robots.tasks"]
    assert set(TASK_FACTORIES) == {spec.key for spec in SPECS}
    expected = {f"stationerybench/{key}" for key in TASK_FACTORIES}
    registry = registered("task")
    assert set(entries) == expected
    assert {name for name in registry if name.startswith("stationerybench/")} == expected
    assert {factory().name for factory in TASK_FACTORIES.values()} == expected
    for key, factory in TASK_FACTORIES.items():
        name = f"stationerybench/{key}"
        assert entries[name] == f"stationerybench.tasks:{key}"
        assert registry[name] is factory
        assert resolve("task", name).name == name


def test_mock_entry_points_resolve_to_named_components() -> None:
    tomllib = pytest.importorskip("tomllib")
    with (ROOT / "pyproject.toml").open("rb") as handle:
        entries = tomllib.load(handle)["project"]["entry-points"]
    assert entries["inspect_robots.embodiments"] == {
        "stationery": "stationerybench.embodiment:StationeryEmbodiment"
    }
    assert entries["inspect_robots.policies"] == {
        "stationery_scripted": "stationerybench.policies:ScriptedStationeryPolicy",
        "stationery_random": "stationerybench.policies:RandomStationeryPolicy",
        "stationery_noop": "stationerybench.policies:NoopStationeryPolicy",
    }
    for group in ("inspect_robots.embodiments", "inspect_robots.policies"):
        for name, reference in entries[group].items():
            module, attribute = reference.split(":")
            component = getattr(import_module(module), attribute)()
            assert component.info.name == name


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.key)
def test_task_contract(spec: TaskSpec) -> None:
    task = TASK_FACTORIES[spec.key]()
    assert isinstance(task, Task)
    assert task.name == f"stationerybench/{spec.key}"
    assert K_TRIALS == 20
    assert MAX_SECONDS == 120.0
    assert task.epochs == Epochs(count=20, reducer="mean")
    assert task.max_seconds == MAX_SECONDS
    assert task.max_steps is None
    assert task.resolve_envelope(10.0).max_steps == 1200
    assert {scorer.name for scorer in task.scorers} == {"task_success", "episode_length"}
    assert task.metadata == {
        "benchmark": "stationerybench",
        "k_trials": 20,
        "protocol": "fixed-setup",
    }
    (scene,) = task.scenes
    assert scene.id == spec.key
    assert scene.instruction == spec.instruction
    assert scene.init_seed == zlib.crc32(spec.key.encode())
    assert scene.metadata == {
        "benchmark": "stationerybench",
        "task": spec.key,
        "title": spec.title,
        "version": spec.version,
        "bimanual": True,
        "objects": list(spec.objects),
        "setup": list(spec.setup),
        "rubric": "\n".join(f"{i} - {line}" for i, line in enumerate(spec.rubric)),
        "rubric_lines": list(spec.rubric),
        "report_slug": spec.report_slug,
    }
    assert isinstance(scene.metadata["rubric"], str)
    assert isinstance(scene.metadata["rubric_lines"], list)
    assert json.loads(json.dumps(dict(scene.metadata))) == scene.metadata
    assert json.loads(json.dumps(dict(task.metadata))) == task.metadata
    assert make_task(spec, max_seconds=90.0).max_seconds == 90.0
    shorter = TASK_FACTORIES[spec.key](max_seconds=90.0)
    assert shorter.max_seconds == 90.0
    assert shorter.resolve_envelope(10.0).max_steps == 900
