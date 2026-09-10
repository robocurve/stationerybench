"""Published task pages and tables preserve the specification text and assets."""

import re
from pathlib import Path

import pytest

from stationerybench import RUBRIC_PRINCIPLES, SPECS, TaskSpec

ROOT = Path(__file__).resolve().parents[1]


def test_index_has_exactly_one_row_per_task() -> None:
    index = (ROOT / "docs/index.md").read_text()
    rows = re.findall(r"^\| `stationerybench/([^`]+)`", index, flags=re.MULTILINE)
    assert rows == [spec.key for spec in SPECS]
    for spec in SPECS:
        assert f"[{spec.title}](tasks/{spec.key}.md)" in index
        assert f"`{spec.report_slug}`" in index
        assert all(obj in index for obj in spec.objects)
    for principle in RUBRIC_PRINCIPLES:
        assert principle in index
    assert "`partial` counts as failure" in index


@pytest.mark.parametrize("spec", SPECS, ids=lambda spec: spec.key)
def test_task_page_and_assets(spec: TaskSpec) -> None:
    path = ROOT / f"docs/tasks/{spec.key}.md"
    assert path.is_file()
    assert (ROOT / f"docs/assets/{spec.key}-setup.jpg").is_file()
    assert (ROOT / f"docs/assets/{spec.key}-human.mp4").is_file()
    page = path.read_text()
    assert page.startswith(f"# {spec.title}\n")
    assert f"![{spec.title} setup](../assets/{spec.key}-setup.jpg)" in page
    assert f"\n> {spec.instruction}\n" in page
    for obj in spec.objects:
        assert f"\n- {obj}\n" in page
    for index, line in enumerate(spec.setup, 1):
        assert f"\n{index}. {line}\n" in page
    for stage, line in enumerate(spec.rubric):
        assert f"\n| {stage} | {line} |\n" in page
    assert f'<video controls width="100%" src="../assets/{spec.key}-human.mp4"></video>' in page


def test_runbook_and_readme_share_commands_and_operator_sequence() -> None:
    readme = (ROOT / "README.md").read_text()
    runbook = (ROOT / "docs/running-on-yam.md").read_text()
    hardware = re.search(r"```bash\n(# from a rig directory.*?)\n```", runbook, re.DOTALL)
    assert hardware is not None
    assert hardware[0] in readme
    bullets = [line for line in runbook.splitlines() if line.startswith("- ")]
    assert len(bullets) == 5
    assert all(line in readme for line in bullets)
    assert "-E auto_start=false" in hardware[1]
    assert "-T max_seconds=90" in readme and "-T max_seconds=90" in runbook
    assert "--no-prompt" in readme
