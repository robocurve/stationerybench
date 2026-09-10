# StationeryBench: package the five stationery tasks as an Inspect Robots benchmark

## Context

The GPT-6 Astra vs MolmoAct2 report ran five bimanual desk-stationery tasks
(marker, lidded box, sticky pads, paper clips, ruler) on the YAM rigs. Every
trial was an ad-hoc `inspect-robots run --instruction ...` launched by
`~/jz/trial.sh`, which supplied the between-trial reset pause, the 0-4 stage
prompt, `trials.csv`, and resume. The task definitions exist only as
free-text instructions in cell manifests plus rubrics in
`~/jz/astra-molmo-report/tasks.json`. Nobody outside this machine can run
"StationeryBench".

Goal: a public, pip-installable `stationerybench` package in the mould of
kitchenbench, so a third party with a YAM rig (or the mock) can
`uv pip install stationerybench` and `inspect-robots run --task stationerybench/<task>`.

### Decisions already made with the user

| Question | Decision |
|---|---|
| Grading | Binary operator y/n, same as kitchenbench. Stage rubrics ship as documentation and scene metadata only. |
| Run loop | Accept inspect-robots' current API (`--epochs N`, per-episode operator gate). No new batch/resume command. |
| Setup variation | One fixed setup per task, N repetitions (`Epochs(count=20, reducer="mean")`). |
| Reporting | None. Whatever `inspect-robots view/inspect` already produces. |
| Template | Slim: kitchenbench packaging skeleton + mock embodiment, no distributions/sim/layout/phone-app scenes. |
| Instruction text | Cleaned `display_instruction` (typos fixed, rig hints removed). |
| Assets | Setup photos in repo as JPG. Human videos: the user chose "linked, not committed" when the .mov sources were quoted at 18-38 MB; the report's converted MP4s are 1.5-2 MB each (8 MB total), so the plan commits those MP4s under docs/assets instead. Flag this substitution to the user. |
| Publishing | Public `github.com/robocurve/stationerybench`, MIT, PyPI trusted publishing, then a worldevals registry PR. |

### Verified facts that shape the plan

- Rigs run PyPI `inspect-robots 0.58.0`, `inspect-robots-yam 0.36.0`,
  `inspect-robots-agent 0.26.0` from `~/robocurve/shared/.venv` (wheels only).
  The local `~/inspect-robots` checkout is at v0.42 and is NOT what runs.
- On 0.58 every attended CLI run is graded by the operator by default,
  registered tasks included (docs/guide/scoring.md on `feat/number-slots`;
  `_build_grader` in cli.py). So a registered task with an operator-reading
  scorer prompts `did the robot succeed? [y/n/partial/skip]` after every
  epoch. `partial` scores as failure.
- `Task` requires exactly one of `max_steps` / `max_seconds`
  (`task.py` on `feat/number-slots`). `max_seconds` resolves against the
  embodiment's `control_hz` (10 Hz on YAM).
- YAM `reset()` gates on "Position the scene, then press Enter to start..."
  only when `auto_start` is false. All rig `config.ini` files set
  `auto_start = true`, so a multi-epoch run would start epoch 2 immediately
  after homing. The README must say `-E auto_start=false`.
- Between epochs the arms hold the home pose under torque. That is the
  reason `run_batch.sh` (inspect-robots-yam PR #143) was reverted. User
  accepted this; the README states it as a safety note.
- `https://openai.robocurve.org/astra-vs-molmoact2/` returns HTTP 401, so
  it cannot be the public home of the videos.
- Kitchenbench's `task_success` scorer (36 lines, `src/kitchenbench/scoring.py`)
  accepts either `termination_reason == "success"` (mock) or an affirmative
  operator verdict (hardware). Reuse verbatim.

## Part A: the `stationerybench` repo (new, `~/jz/stationerybench`)

### Layout

```
stationerybench/
├── README.md  CHANGELOG.md  CLAUDE.md  CITATION.cff  LICENSE (MIT)
├── pyproject.toml  uv.lock  mkdocs.yml  .pre-commit-config.yaml  .gitignore
├── plans/0001-stationerybench.md          (this plan, repo convention)
├── src/stationerybench/
│   ├── __init__.py        re-exports + __version__ (copy kitchenbench pattern)
│   ├── specs.py           TaskSpec dataclass + the 5 SPECS (single source of truth)
│   ├── tasks.py           make_task(), one @task factory per spec, TASK_FACTORIES
│   ├── scoring.py         task_success  (copy of kitchenbench/scoring.py)
│   ├── embodiment.py      StationeryEmbodiment mock (kitchenbench/embodiment.py minus realize_scene)
│   ├── policies.py        Scripted/Random/Noop (kitchenbench/policies.py, renamed)
│   ├── py.typed  CLAUDE.md
├── docs/
│   ├── index.md           task table + how grading works
│   ├── running-on-yam.md  the hardware runbook
│   ├── tasks/<key>.md     one page per task: photo, objects, setup, instruction, rubric, video link
│   └── assets/<key>-setup.jpg   (5 files, ~300 KB each)
├── tests/
│   ├── test_specs.py  test_tasks.py  test_conformance.py  test_eval.py  test_docs.py
└── .github/workflows/{ci,docs,release}.yml   (copied from kitchenbench; canary.yml skipped for now)
```

### `specs.py`

```python
@dataclass(frozen=True)
class TaskSpec:
    key: str                 # registry suffix: stationerybench/<key>
    title: str
    instruction: str         # the Scene instruction, sent to the policy verbatim
    objects: tuple[str, ...] # shopping list
    setup: tuple[str, ...]   # operator reset checklist, one line each
    rubric: tuple[str, ...]  # 5 lines, stage 0..4; stage 4 == binary success
    report_slug: str         # slug used in the Astra vs MolmoAct2 report
    version: int = 1
```

Table-side layout convention for every task: operator faces the bench, the
two arm bases are at the far edge, "left"/"right" are the operator's left and
right (matches the rig `run` docs). Objects go within reach of both arms
unless a line says otherwise.

The five specs (copy authored here; implementer places it verbatim):

**`uncap_marker`** ("Uncap the marker", report slug `pen`)
- instruction: `Pull the cap off the sharpie and place them separately on the table.`
- objects: `black Sharpie fine-point permanent marker, capped`
- setup: `Cap the marker fully.` / `Lay it flat at the centre of the bench, roughly midway between the two arm bases, aligned front-to-back with the cap toward the arms.`
- rubric: the 5 lines from tasks.json `pen`.

**`eraser_from_box`** ("Open the box, take out an eraser, close the lid", slug `lid`)
- instruction: `Open the lid of the box, take out one eraser from the box and place it on the table, then close the box. The lid is a lift-open lid, so it may be easier to just prop it open with the gripper.`
- objects: `cloth-covered book-style box with a hinged lift lid (about 30 x 22 x 7 cm)`, `one block eraser in its paper sleeve`
- setup: `Place the box at the centre of the bench with the hinge at the far edge, toward the arms.` / `Put the eraser inside, resting on the floor of the box near the front-left corner.` / `Close the lid fully. (The reference photo shows the box open so the eraser is visible.)`
- rubric: tasks.json `lid`.

**`middle_sticky_pad`** ("Pull the middle sticky pad from a stack", slug `sticky`)
- instruction: `There is a stack of three sticky notes. Take the middle one out and put it on the table. Make sure everything is at rest at the end, but do not let the top one touch the table at all, so it should rest on one of the sticky notes at the end.`
- objects: `three shrink-wrapped 3 x 3 inch sticky-note cubes (Post-it Super Sticky notes cube or equivalent)`
- setup: `Stack the three pads vertically at the centre of the bench.` / `Offset each pad slightly (about 1 cm and a few degrees of yaw) from the one below so the edges are not flush.`
- rubric: tasks.json `sticky`.

**`pour_paperclips`** ("Pour paper clips into a lifted bowl", slug `paperclip`)
- instruction: `Lift the left bowl in the air and pour some paper clips from the paper clip box into the bowl.`
- objects: `one light ceramic bowl about 15 cm across`, `an open cardboard box of steel paper clips, roughly half full`
- setup: `Place the bowl upright on the left half of the bench, about a bowl-width in from the left arm base.` / `Place the open paper clip box on the right half, about level with the bowl, opening facing up.`
- rubric: tasks.json `paperclip`.

**`ruler_handover`** ("Hand a ruler between arms, cup to cup", slug `ruler`)
- instruction: `Transfer the ruler from the left cup to the right cup, but you must hand it over to the other arm's gripper in mid-air.`
- objects: `two paper cups (about 12 oz)`, `one clear plastic 12 inch (30 cm) ruler`
- setup: `Stand one cup near the left arm and one near the right arm, at the same distance from the arm bases, so the ruler cannot be moved without a handover.` / `Stand the ruler in the left cup, leaning toward the far edge of the bench.` / `Leave the right cup empty.`
- rubric: tasks.json `ruler`.

A `RUBRIC_PRINCIPLES` tuple holds the three `rubric_principles` strings from
tasks.json, for the docs page.

### `tasks.py`

```python
K_TRIALS = 20            # published protocol: 20 repetitions per task per model
MAX_SECONDS = 120.0      # 1200 steps at 10 Hz, the published VLA horizon

def make_task(spec: TaskSpec, *, max_seconds: float = MAX_SECONDS) -> Task:
    scene = Scene(
        id=spec.key,
        instruction=spec.instruction,
        init_seed=zlib.crc32(spec.key.encode()),
        metadata={
            "benchmark": "stationerybench", "task": spec.key, "title": spec.title,
            "version": spec.version, "bimanual": True,
            "objects": list(spec.objects), "setup": list(spec.setup),
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
```

One `@task("stationerybench/<key>")` factory per spec taking
`max_seconds: float = MAX_SECONDS` so `-T max_seconds=90` reproduces the
published agent horizon (900 steps). `--epochs N` already overrides the count.
`TASK_FACTORIES: dict[str, Callable[..., Task]]` mirrors kitchenbench for tests.

### Mock embodiment and policies

Copy `kitchenbench/embodiment.py` and `policies.py`, rename to
`StationeryEmbodiment` / `stationery_scripted|random|noop`, embodiment name
`stationery`, and delete the `realize_scene` branch in `reset()` (fixed
setups: the instruction is `scene.instruction`). Keep `SEEDABLE, RENDERABLE,
PRIVILEGED_SUCCESS` so `assert_embodiment_conformant` passes.

### `pyproject.toml`

Copy kitchenbench's, then: name `stationerybench`, description "Five bimanual
desk-stationery manipulation tasks for VLA models and LLM agents, built on
Inspect Robots.", keywords, URLs, `dependencies = ["inspect-robots>=0.58", "numpy>=1.24"]`
(0.58 is the floor where registered tasks are operator-graded by default;
the README's hardware runbook relies on that).

Every `kitchenbench` path in the file must be rewritten or the slim repo
fails its own gates (verified against `~/jz/kitchenbench/pyproject.toml`):
- line 74 `[tool.hatch.build.targets.wheel] packages = ["src/stationerybench"]` (else an empty wheel)
- line 102 `[tool.ruff.lint.isort] known-first-party = ["stationerybench"]`
- line 110 `[tool.mypy] files = ["src/stationerybench"]`
- line 119 `[tool.coverage.run] source = ["stationerybench"]`
- lines 46-47: delete `[project.scripts]` (no layout CLI)
- line 26: drop `jsonschema>=4.21` from `dev` (only layout code used it)

Entry points:

```toml
[project.entry-points."inspect_robots.tasks"]
"stationerybench/uncap_marker"      = "stationerybench.tasks:uncap_marker"
"stationerybench/eraser_from_box"   = "stationerybench.tasks:eraser_from_box"
"stationerybench/middle_sticky_pad" = "stationerybench.tasks:middle_sticky_pad"
"stationerybench/pour_paperclips"   = "stationerybench.tasks:pour_paperclips"
"stationerybench/ruler_handover"    = "stationerybench.tasks:ruler_handover"
[project.entry-points."inspect_robots.embodiments"]
stationery = "stationerybench.embodiment:StationeryEmbodiment"
[project.entry-points."inspect_robots.policies"]
stationery_scripted = "stationerybench.policies:ScriptedStationeryPolicy"
stationery_random   = "stationerybench.policies:RandomStationeryPolicy"
stationery_noop     = "stationerybench.policies:NoopStationeryPolicy"
```

Keep ruff (incl. D1), mypy strict, pytest `fail_under = 100`, hatch-vcs,
hatch-fancy-pypi-readme.

`mkdocs.yml`: copy, then set `site_name: StationeryBench`, `site_url`,
`repo_url`, `repo_name`, `site_description`, a stationery logo icon, and
rewrite `nav` to `index.md`, `running-on-yam.md`, and the five
`tasks/<key>.md` pages. The copied nav points at `layouts.md`, which does
not exist here, and `mkdocs build --strict` runs inside ci.yml's required
`quality` job.

`uv.lock`: do NOT copy kitchenbench's (it pins inspect-robots 0.6.0). Run
`uv lock` once `pyproject.toml` is final and commit the result. All three
workflows run `uv sync --locked` and fail without a current lockfile.

### Tests (all against the mock, no hardware)

- `test_specs.py`: 5 specs, unique keys and report slugs, each rubric has
  exactly 5 lines, instructions contain no `{`/`}` and none of the known
  typos (`Lieft`, `juset`, `arms'`), no rig hint substring `rotate the joints`.
- `test_tasks.py`: factories == spec keys; entry-point names ==
  `@task` names == `Task.name`; one scene per task; `epochs == Epochs(20, "mean")`;
  scorer names `{"task_success", "episode_length"}`; scene metadata is
  JSON-native; `make_task(spec, max_seconds=90.0).max_seconds == 90.0`.
- `test_conformance.py`: `assert_embodiment_conformant(StationeryEmbodiment().info)`.
- `test_eval.py`: `inspect_robots.eval()` has no `epochs` kwarg in 0.58
  (the CLI does `dataclasses.replace(task, epochs=N)`), so the test builds
  `replace(make_task(spec), epochs=2)` and calls
  `eval(task, "stationery_scripted", "stationery", sinks=[], store_actions=False)`.
  `sinks=[]` and `store_actions=False` keep the test from writing `logs/`
  and `logs/actions/` into the repo. Scripted succeeds on all 5 (reduced
  `task_success == 1.0`); `stationery_noop` gives 0.0. Also `task_success`
  unit cases: termination success, verdict `"y"`, verdict `"partial"`
  (False), None.
- `test_docs.py`: `docs/tasks/<key>.md` and `docs/assets/<key>-setup.jpg`
  exist for every spec; the `docs/index.md` table has exactly one row per
  `stationerybench/<key>`; each task page contains the spec's instruction
  verbatim (drift guard).

### Docs and README

- `docs/index.md`: task table (`--task`, goal, objects, report slug), the
  grading section (binary; rubric stage 4 == success; `partial` counts as
  failure), `RUBRIC_PRINCIPLES`.
- `docs/tasks/<key>.md` generated from the spec by hand once (the drift test
  keeps it honest): photo, objects, setup checklist, instruction, rubric
  table (stage 0-4), link to the human demo video on the GitHub release.
- `docs/running-on-yam.md` and README "Run it on real hardware":

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

  Explain the operator sequence exactly as 0.58 + yam 0.36 run it:
  - Epoch 1 only: "Arms will move to the home pose - stand clear, then press
    Enter..." (once per connection).
  - Every epoch: arms ramp to home, then "Position the scene, then press
    Enter to start..." That gate is the reset pause and exists only because
    of `-E auto_start=false` (rig configs default `auto_start = true`, which
    would start the next epoch straight after homing). Reset the objects
    only after the arms have stopped at home.
  - After every episode: the rubric text, then
    `did the robot succeed? [y/n/partial/skip]` and an optional note.
    `partial` scores as failure.
  - The arms hold the home pose under torque while you reset. Keep clear of
    the arms and keep the e-stop in reach.
  - One log JSON per run holds all 20 epochs (`inspect-robots view logs/`).
  Note deviations from the
  published report: instruction wording was cleaned, the agent condition
  used a 90 s horizon (`-T max_seconds=90`), and the report graded a 0-4
  stage from video whereas this package records the operator's binary verdict.
- README quick start mirrors kitchenbench: install, `list tasks`, run on the
  mock with `stationery_scripted`. Any mock command that does not succeed
  (`stationery_noop`, `stationery_random`) must carry `--no-prompt`:
  on a TTY the default operator grader prompts after every non-definitive
  epoch, and the mock never emits a `failure` termination.
- `CITATION.cff`, `CHANGELOG.md` (0.1.0), `CLAUDE.md` (adapted from
  kitchenbench's: gates, PyPI-only dependency, where the copy lives).

### Assets

- `docs/assets/<key>-setup.jpg`: from `~/jz/<slug>_setup.png` (1690x1262),
  JPEG quality 85, target under 400 KB each. Mapping pen→uncap_marker,
  lid→eraser_from_box, sticky→middle_sticky_pad, paperclip→pour_paperclips,
  ruler→ruler_handover.
- Human videos: copy `~/jz/astra-molmo-report/video/<slug>-human.mp4`
  (1.5-2 MB each) to `docs/assets/<key>-human.mp4`; task pages embed them
  with an HTML `<video>` tag (mkdocs-material passes raw HTML through) and
  README links to the docs pages. No release assets needed.

## Part B: inspect-robots and inspect-robots-yam

**No code changes required** for the agreed scope. The installed 0.58/0.36
stack already provides operator grading of registered tasks, per-epoch reset
gating via `auto_start=false`, task-level `--epochs`, and log viewing.

Documented in the README instead of changed in code:
- `auto_start=true` in rig configs skips the reset gate; multi-epoch
  benchmark runs need `-E auto_start=false`.
- Arms stay torqued at home between epochs.

Optional follow-ups, out of scope, listed in the plan file for later:
1. inspect-robots-yam: when the task declares `epochs > 1`, gate
   "Position the scene" before every epoch even with `auto_start=true`
   (auto_start was designed for single ad-hoc runs).
2. inspect-robots docs: a cookbook page "Running a fixed-setup benchmark with
   operator grading" (StationeryBench as the worked example).
3. A CSV/JSON export across a log dir, if the trial.sh/report.py workflow is
   ever to be retired.

## Part C: worldevals registration (separate PR, after v0.1.0 is on PyPI)

Add `src/worldevals/register/stationerybench/eval.yaml` following
`register/kitchenbench/eval.yaml` (schema_version 1, status `alpha`,
`access: public`, `package.distribution: stationerybench`,
`requires_inspect_robots: ">=0.58"`, `repository_commit` pinned to the v0.1.0
tag commit, 5 `tasks` entries), plus `src/worldevals/stationerybench.py`
mirroring `kitchenbench.py`, and whatever registry tests worldevals runs
(`worldevals validate stationerybench`, `worldevals check stationerybench --installed`).

## Execution

1. `mkdir ~/jz/stationerybench && git init`; copy skeleton files from
   `~/jz/kitchenbench` (workflows, pre-commit, mkdocs.yml, LICENSE, .gitignore).
2. Write `plans/0001-stationerybench.md` (this plan), run one fresh-context
   critique subagent, fix, repeat until clean.
3. Dispatch `codex-implementer` for the package, tests, docs skeleton and
   workflows, with the spec copy above supplied verbatim. Codex writes files
   only, no git.
4. Fable reviews the diff (specs text verbatim, no test weakening), converts
   the photos, copies the MP4s, then `uv lock` and the gates:
   `uv sync --locked --extra dev --extra docs && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest --cov && uv run mkdocs build --strict`.
   Commit `uv.lock`.
5. `gh repo create robocurve/stationerybench --public`, push `main`, open the
   initial PR, wait for `ci-ok`, merge. Enable Pages (source: GitHub Actions).
6. Cut `v0.1.0` via the Release workflow.
7. worldevals PR (Part C).

**Blockers only the user can clear:** PyPI trusted-publisher configuration for
the new project (`pypi` environment, publisher `robocurve/stationerybench`
workflow `release.yml`). `gh` is already authenticated with access to the
robocurve org, so repo creation and Pages should not block. Everything else
proceeds without pausing.

## Verification

- Local gates listed in step 4 all green, coverage 100%.
- Fresh venv: `uv venv /tmp/sb && uv pip install --python /tmp/sb/bin/python ~/jz/stationerybench`;
  `inspect-robots list tasks` shows the 5 tasks;
  `inspect-robots run --task stationerybench/uncap_marker --policy stationery_scripted --embodiment stationery --epochs 2`
  exits 0 with `task_success = 1.0`; the same with `--policy stationery_noop --no-prompt`
  gives 0.0 (without `--no-prompt` it would block on the operator prompt).
- Rig dry run, no motion: in `~/robocurve/rig-4`,
  `RIG_RUN_DRY=1 ./run --task stationerybench/uncap_marker --epochs 2 -E auto_start=false`
  prints the intended launch. A live trial on hardware is the user's call and
  is not part of this plan.
- After release: `uv pip install stationerybench==0.1.0` resolves from PyPI;
  docs site builds and each task page plays its video.
