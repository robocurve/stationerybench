# StationeryBench: agent guide

StationeryBench is a standalone Inspect Robots benchmark plugin: five bimanual
stationery tasks, each with one fixed scene and 20 mean-reduced trials. Tasks
define the setup, instruction, and scoring; compatible policy and embodiment
pairs provide execution.

## Repository map

- `src/stationerybench/`: package; see `src/stationerybench/CLAUDE.md`.
- `tests/`: specs, registry, conformance, mock evaluation, and documentation checks.
- `docs/`: task pages, final setup photos and MP4 demonstrations, and the YAM runbook.
- `plans/0001-stationerybench.md`: approved implementation and protocol plan.
- `README.md`: installation, mock quick start, hardware operation, and citation.

## Working here

- Inspect Robots comes from PyPI (`inspect-robots>=0.58`), not a local checkout.
  The rig's installed 0.58 API is the compatibility baseline; a local framework
  checkout can be stale. Use public top-level imports where available. Capability
  flags and conformance helpers live in their respective framework submodules.
- Conda gotcha: `uv pip install` targets the active environment. Activate the
  intended `.venv` and set `VIRTUAL_ENV="$PWD/.venv"`, or use `uv run`, rather than
  accidentally installing into conda base.
- Public modules, classes, and functions need contract docstrings (Ruff D1).
- Keep numbered plans in `plans/NNNN-description.md`. Read the relevant approved
  plan before changing the protocol; do not silently alter authored task text.
- `specs.py` is the source of truth. Keep the documentation drift tests current.
- Real YAM and model adapters live in their own packages. This repository ships
  tasks and an abstract mock.

## Gates

```bash
uv sync --locked --extra dev --extra docs && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest --cov && uv run mkdocs build --strict
```

Mypy is strict and coverage must remain 100%. Pre-commit runs hygiene checks,
Ruff, and mypy; pre-push runs the coverage gate. The strict documentation build
runs in CI's quality job. Tests use `sinks=[]` and `store_actions=False` to avoid
writing logs, and suppress the framework's git provenance probe.

## CI and releases

- CI uses `uv sync --locked`; maintainers regenerate and commit `uv.lock` after
  changing dependencies.
- `ci-ok` aggregates quality and tests. Add any required new job to its `needs`.
- The intended workflow is PR-only main with `ci-ok` required. The red-main job
  opens an issue when CI fails on a push to main.
- Releases derive their version from tags through hatch-vcs; keep the project
  version dynamic. The release workflow publishes through PyPI trusted publishing.
- MkDocs Material publishes through GitHub Pages. The PyPI README is transformed
  by hatch-fancy-pypi-readme to render GitHub alert syntax as bold blockquotes.

## Public writing

Use concrete language and contract descriptions. Avoid decorative emoji,
slogans, and unnecessary emphasis. Preserve verbatim rubric and instruction
text, commands, links, numbers, and safety qualifiers when editing prose.
