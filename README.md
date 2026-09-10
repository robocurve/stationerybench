# StationeryBench

Five bimanual desk-stationery manipulation tasks for VLA models and LLM agents,
built on [Inspect Robots](https://github.com/robocurve/inspect-robots).

The five tasks cover uncapping a marker, retrieving an eraser from a box,
extracting a sticky pad, pouring paper clips, and handing over a ruler.
Each has one fixed setup, 20 repetitions, and a binary success score.
Setup photos, checklists, verbatim instructions, stage rubrics, and human
MP4 demonstrations are in the [task reference](https://robocurve.github.io/stationerybench/).

## Quick start

Install from PyPI and run two trials on the bundled mock:

```bash
uv pip install stationerybench
inspect-robots list tasks
inspect-robots run --task stationerybench/uncap_marker --policy stationery_scripted --embodiment stationery --epochs 2
```

Installation registers five tasks, the `stationery` embodiment, and three
mock policies. The mock models progress toward a seeded goal, without physics.
The scripted oracle reads privileged state and succeeds; it exercises the
evaluation pipeline and does not measure a real model's manipulation ability.

`stationery_noop` and `stationery_random` need `--no-prompt` for unattended mock
runs. Without it, a terminal can prompt for an operator verdict after every
non-definitive epoch; the mock never emits a failure termination.

```bash
inspect-robots run --task stationerybench/uncap_marker --policy stationery_noop --embodiment stationery --epochs 2 --no-prompt
```

## The tasks

| Task (`--task`) | Goal | Objects | Report slug |
|---|---|---|---|
| `stationerybench/uncap_marker` | [Uncap the marker](docs/tasks/uncap_marker.md) | black Sharpie fine-point permanent marker, capped | `pen` |
| `stationerybench/eraser_from_box` | [Open the box, take out an eraser, close the lid](docs/tasks/eraser_from_box.md) | cloth-covered book-style box with a hinged lift lid (about 30 x 22 x 7 cm); one block eraser in its paper sleeve | `lid` |
| `stationerybench/middle_sticky_pad` | [Pull the middle sticky pad from a stack](docs/tasks/middle_sticky_pad.md) | three shrink-wrapped 3 x 3 inch sticky-note cubes (Post-it Super Sticky notes cube or equivalent) | `sticky` |
| `stationerybench/pour_paperclips` | [Pour paper clips into a lifted bowl](docs/tasks/pour_paperclips.md) | one light ceramic bowl about 15 cm across; an open cardboard box of steel paper clips, roughly half full | `paperclip` |
| `stationerybench/ruler_handover` | [Hand a ruler between arms, cup to cup](docs/tasks/ruler_handover.md) | two paper cups (about 12 oz); one clear plastic 12 inch (30 cm) ruler | `ruler` |

The operator faces the bench, with the two arm bases at the far edge.
Left and right are the operator's left and right. Objects go within reach
of both arms unless a setup line says otherwise.

## Run it on real hardware (YAM arms)

Use a rig configured with Inspect Robots 0.58 or later and the YAM adapter
(the operator sequence below describes inspect-robots 0.58 with
inspect-robots-yam 0.36). The rig's `./run` and `config.ini` supply the hardware
and policy configuration; the mock policies are for the abstract mock only.

```bash
# from a rig directory with ./run and config.ini
uv pip install stationerybench        # into the rig venv
inspect-robots list tasks             # shows stationerybench/*
# VLA (MolmoAct2 /act server running):
./run --task stationerybench/uncap_marker --epochs 20 -E auto_start=false
# LLM agent:
./run --task stationerybench/uncap_marker --epochs 20 -E auto_start=false \
  --policy agent -P model=... -P wire=... -E control_interface=eef_pos
```

- Epoch 1 only: "Arms will move to the home pose - stand clear, then press Enter..." (once per connection).
- Every epoch: arms ramp to home, then "Position the scene, then press Enter to start..." That gate is the reset pause and exists only because of `-E auto_start=false` (rig configs default `auto_start = true`, which would start the next epoch straight after homing). Reset the objects only after the arms have stopped at home.
- After every episode: the rubric text, then `did the robot succeed? [y/n/partial/skip]` and an optional note. `partial` scores as failure.
- The arms hold the home pose under torque while you reset. Keep clear of the arms and keep the e-stop in reach.
- One log JSON per run holds all 20 epochs (`inspect-robots view logs/`).

## Differences from the published report

Instruction wording was cleaned: typos were fixed and rig hints removed.
The default 120 s horizon matches the report's VLA condition (1200 steps at
10 Hz). The agent condition used a 90 s horizon (900 steps); add
`-T max_seconds=90` to reproduce it. The report graded a 0-4 stage from video,
whereas this package records the operator's binary verdict. Stage 4 is success;
`partial` counts as failure. The rubrics remain available for reference, but
this package does not record a numeric stage or provide the report's CSV/resume
workflow.

## Development

Inspect Robots is consumed from PyPI (`inspect-robots>=0.58`). After dependency
changes, regenerate `uv.lock` before running the locked CI gates:

```bash
uv sync --locked --extra dev --extra docs && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest --cov && uv run mkdocs build --strict
```

Coverage must be 100%, mypy is strict, and Ruff D1 requires contract docstrings
for public modules, classes, and functions. See [CLAUDE.md](CLAUDE.md) for
repository conventions.

## Citation

```bibtex
@software{stationerybench,
  author  = {RoboCurve},
  title   = {StationeryBench: Five bimanual desk-stationery manipulation tasks for VLA models and LLM agents},
  year    = {2026},
  url     = {https://github.com/robocurve/stationerybench},
  version = {0.1.0},
  license = {MIT}
}
```

[MIT license](LICENSE).
