# `stationerybench`: module map

Importing the package registers five task factories. Installed entry points
make tasks, the mock embodiment, and the policies discoverable without importing.

| Module | Contract |
|---|---|
| `specs.py` | Frozen `TaskSpec`, ordered `SPECS`, `SPEC_BY_KEY`, and verbatim `RUBRIC_PRINCIPLES`. |
| `tasks.py` | One fixed `Scene` per task, 20 mean-reduced trials, configurable 120-second limit, five factories, and `TASK_FACTORIES`. |
| `scoring.py` | `task_success()` reads success termination or an affirmative recorded operator verdict; partial is failure. |
| `embodiment.py` | `StationeryEmbodiment` models seeded goal-aligned progress with eight action dimensions; preserves `scene.instruction` on every observation. |
| `policies.py` | `ScriptedStationeryPolicy` follows privileged `goal_dir`; random and noop policies provide baselines. All emit action chunks. |
| `__init__.py` | Public re-exports and distribution version with a fallback for uninstalled source trees. |

## Invariants

- Entry-point name, `@task` name, and returned `Task.name` match exactly:
  `stationerybench/<key>`.
- Scene metadata is JSON-native. `rubric` is a non-blank string so inspect-robots
  0.58 displays it before the operator verdict; `rubric_lines` is a list.
- The task declares `max_seconds`, never both horizon fields. Change repetitions
  with `dataclasses.replace(task, epochs=Epochs(count=N, reducer="mean"))`;
  inspect-robots 0.58 `eval()` has no `epochs` argument.
- The mock declares `SEEDABLE`, `RENDERABLE`, and `PRIVILEGED_SUCCESS`. Its action
  space is `[left dx, dy, dz, right dx, dy, dz, left gripper, right gripper]`.
  Keep bounds and dimension labels conformant, and alignment threshold at 0.99.
- Mock policies pair with the mock's eight-dimensional action space. Hardware
  uses its own compatible policies; tasks themselves have no action space.
- Evaluation tests pass component instances so they also work via `PYTHONPATH=src`.
  The caller closes a caller-owned embodiment.

## Adding or changing a task

1. Update the approved plan, then author a frozen spec with a concrete instruction,
   objects, reset checklist, five rubric stages, and a unique report slug.
2. Add the factory, `TASK_FACTORIES` entry, public export, and matching entry point.
3. Add its task page, assets, index and README table rows, and MkDocs navigation.
4. Keep specs, task names, documentation, conformance, and eval tests passing with
   100% coverage. Rubric stage 4 remains the binary success criterion.
