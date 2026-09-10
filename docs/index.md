# StationeryBench

Five bimanual desk-stationery manipulation tasks for VLA models and LLM agents,
built on [Inspect Robots](https://github.com/robocurve/inspect-robots).
Each task supplies a fixed setup, an instruction, and a five-stage rubric.
The tasks run with compatible policy and embodiment pairs, including the
bundled abstract mock and real YAM arms.

For installation and the mock quick start, see the
[README](https://github.com/robocurve/stationerybench#readme).
For hardware, follow [Running on YAM arms](running-on-yam.md).

## The tasks

| Task (`--task`) | Goal | Objects | Report slug |
|---|---|---|---|
| `stationerybench/uncap_marker` | [Uncap the marker](tasks/uncap_marker.md) | black Sharpie fine-point permanent marker, capped | `pen` |
| `stationerybench/eraser_from_box` | [Open the box, take out an eraser, close the lid](tasks/eraser_from_box.md) | cloth-covered book-style box with a hinged lift lid (about 30 x 22 x 7 cm); one block eraser in its paper sleeve | `lid` |
| `stationerybench/middle_sticky_pad` | [Pull the middle sticky pad from a stack](tasks/middle_sticky_pad.md) | three shrink-wrapped 3 x 3 inch sticky-note cubes (Post-it Super Sticky notes cube or equivalent) | `sticky` |
| `stationerybench/pour_paperclips` | [Pour paper clips into a lifted bowl](tasks/pour_paperclips.md) | one light ceramic bowl about 15 cm across; an open cardboard box of steel paper clips, roughly half full | `paperclip` |
| `stationerybench/ruler_handover` | [Hand a ruler between arms, cup to cup](tasks/ruler_handover.md) | two paper cups (about 12 oz); one clear plastic 12 inch (30 cm) ruler | `ruler` |

## Layout convention

The operator faces the bench, with the two arm bases at the far edge.
Left and right are the operator's left and right. Objects go within reach
of both arms unless a setup line says otherwise.

## Grading

Each task uses one fixed setup, repeated for 20 trials by default. The mean
of the binary `task_success` scores is the completion rate. The default horizon
is 120 seconds (1200 steps at the YAM control rate of 10 Hz).

Rubric stage 4 means success: the instruction is fully satisfied. On hardware,
the rubric is shown to the operator before the verdict prompt. Answer `y` for
success and `n` for failure; `partial` counts as failure. The scorer accepts a
success termination or an affirmative recorded operator verdict. In the mock,
the scripted policy produces the privileged success termination.

### Rubric principles

- 0 - nothing purposeful, 1 - deliberate contact with the target object(s), 2 - a secure grasp, 3 - the task's core manipulation achieved, 4 - the instruction fully satisfied.
- Every stage is a precondition of the next, and is a state that persists long enough to be judged from the video.
- A completed trial means stage 4, completion rate is the share of trials at stage 4. Mean stage summarises partial progress.
