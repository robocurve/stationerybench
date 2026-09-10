# Running on YAM arms

Use a rig configured with Inspect Robots 0.58 or later and the YAM adapter
(the operator sequence below describes inspect-robots 0.58 with
inspect-robots-yam 0.36). The rig's `./run` and `config.ini` supply the hardware
and policy configuration; the mock policies are for the abstract mock only.

```bash
# from a rig directory with ./run and config.ini
uv pip install "stationerybench @ git+https://github.com/robocurve/stationerybench"  # into the rig venv
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

Use each [task page](index.md#the-tasks) for its reset checklist.

The operator faces the bench, with the two arm bases at the far edge.
Left and right are the operator's left and right. Objects go within reach
of both arms unless a setup line says otherwise.

## Differences from the published report

Instruction wording was cleaned: typos were fixed and rig hints removed.
The default 120 s horizon matches the report's VLA condition (1200 steps at
10 Hz). The agent condition used a 90 s horizon (900 steps); add
`-T max_seconds=90` to reproduce it. The report graded a 0-4 stage from video,
whereas this package records the operator's binary verdict. Stage 4 is success;
`partial` counts as failure. The rubrics remain available for reference, but
this package does not record a numeric stage or provide the report's CSV/resume
workflow.
