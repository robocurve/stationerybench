"""The five immutable specifications contain concrete, cleaned instructions."""

from dataclasses import FrozenInstanceError
from importlib import metadata, reload
from unittest.mock import patch

import pytest

import stationerybench
from stationerybench import RUBRIC_PRINCIPLES, SPEC_BY_KEY, SPECS, TaskSpec


def test_spec_identity_and_order() -> None:
    assert [spec.key for spec in SPECS] == [
        "uncap_marker",
        "eraser_from_box",
        "middle_sticky_pad",
        "pour_paperclips",
        "ruler_handover",
    ]
    assert [spec.report_slug for spec in SPECS] == ["pen", "lid", "sticky", "paperclip", "ruler"]
    assert len({spec.key for spec in SPECS}) == len(SPECS) == 5
    assert len({spec.report_slug for spec in SPECS}) == 5
    assert {spec.key: spec for spec in SPECS} == SPEC_BY_KEY
    assert isinstance(SPECS, tuple)
    assert isinstance(RUBRIC_PRINCIPLES, tuple)
    assert len(RUBRIC_PRINCIPLES) == 3
    assert all(isinstance(line, str) and line for line in RUBRIC_PRINCIPLES)


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.key)
def test_spec_contract(spec: TaskSpec) -> None:
    assert spec.title and spec.instruction
    assert spec.version == 1
    for lines in (spec.objects, spec.setup, spec.rubric):
        assert isinstance(lines, tuple)
        assert lines and all(isinstance(line, str) and line for line in lines)
    assert len(spec.rubric) == 5
    for forbidden in ("{", "}", "Lieft", "juset", "arms'", "rotate the joints"):
        assert forbidden not in spec.instruction
    with pytest.raises(FrozenInstanceError):
        spec.title = "changed"


def test_version_from_distribution_metadata() -> None:
    try:
        with patch.object(metadata, "version", return_value="0.1.0") as version:
            assert reload(stationerybench).__version__ == "0.1.0"
            version.assert_called_once_with("stationerybench")
    finally:
        reload(stationerybench)


def test_version_fallback_for_uninstalled_source() -> None:
    try:
        with patch.object(metadata, "version", side_effect=metadata.PackageNotFoundError):
            assert reload(stationerybench).__version__ == "0.0.0+unknown"
    finally:
        reload(stationerybench)
