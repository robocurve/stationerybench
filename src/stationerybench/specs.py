"""Fixed task definitions and the report's verbatim stage rubrics.

The operator faces the bench with both arm bases at the far edge. Left and
right mean the operator's left and right. Objects are within reach of both
arms unless a setup line says otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    """An immutable task with a fixed reset checklist and five rubric stages."""

    key: str
    title: str
    instruction: str
    objects: tuple[str, ...]
    setup: tuple[str, ...]
    rubric: tuple[str, ...]
    report_slug: str
    version: int = 1


SPECS: tuple[TaskSpec, ...] = (
    TaskSpec(
        key="uncap_marker",
        title="Uncap the marker",
        instruction="Pull the cap off the sharpie and place them separately on the table.",
        objects=("black Sharpie fine-point permanent marker, capped",),
        setup=(
            "Cap the marker fully.",
            (
                "Lay it flat at the centre of the bench, roughly midway between the two "
                "arm bases, aligned front-to-back with the cap toward the arms."
            ),
        ),
        rubric=(
            "No purposeful contact with the marker",
            "Touches or moves the marker deliberately",
            "Holds the marker securely in one gripper",
            "Cap separated from the body, either part still held",
            "Cap and body both released on the table",
        ),
        report_slug="pen",
    ),
    TaskSpec(
        key="eraser_from_box",
        title="Open the box, take out an eraser, close the lid",
        instruction=(
            "Open the lid of the box, take out one eraser from the box and place it on "
            "the table, then close the box. The lid is a lift-open lid, so it may be "
            "easier to just prop it open with the gripper."
        ),
        objects=(
            "cloth-covered book-style box with a hinged lift lid (about 30 x 22 x 7 cm)",
            "one block eraser in its paper sleeve",
        ),
        setup=(
            (
                "Place the box at the centre of the bench with the hinge at the far "
                "edge, toward the arms."
            ),
            "Put the eraser inside, resting on the floor of the box near the front-left corner.",
            (
                "Close the lid fully. (The reference photo shows the box open so the "
                "eraser is visible.)"
            ),
        ),
        rubric=(
            "No purposeful contact with the box or lid",
            "Touches the lid deliberately",
            "Lid held open far enough to reach inside",
            "Eraser lifted out of the box",
            "Eraser released on the table outside the box and the lid closed",
        ),
        report_slug="lid",
    ),
    TaskSpec(
        key="middle_sticky_pad",
        title="Pull the middle sticky pad from a stack",
        instruction=(
            "There is a stack of three sticky notes. Take the middle one out and put it "
            "on the table. Make sure everything is at rest at the end, but do not let "
            "the top one touch the table at all, so it should rest on one of the sticky "
            "notes at the end."
        ),
        objects=(
            (
                "three shrink-wrapped 3 x 3 inch sticky-note cubes (Post-it Super "
                "Sticky notes cube or equivalent)"
            ),
        ),
        setup=(
            "Stack the three pads vertically at the centre of the bench.",
            (
                "Offset each pad slightly (about 1 cm and a few degrees of yaw) from "
                "the one below so the edges are not flush."
            ),
        ),
        rubric=(
            "No purposeful contact with the stack",
            "Touches or moves a pad deliberately",
            "Top pad lifted clear of the stack",
            "Middle pad removed from the stack and released on the table",
            "Middle pad on the table, top pad resting on a pad and not on the table",
        ),
        report_slug="sticky",
    ),
    TaskSpec(
        key="pour_paperclips",
        title="Pour paper clips into a lifted bowl",
        instruction=(
            "Lift the left bowl in the air and pour some paper clips from the paper "
            "clip box into the bowl."
        ),
        objects=(
            "one light ceramic bowl about 15 cm across",
            "an open cardboard box of steel paper clips, roughly half full",
        ),
        setup=(
            (
                "Place the bowl upright on the left half of the bench, about a "
                "bowl-width in from the left arm base."
            ),
            (
                "Place the open paper clip box on the right half, about level with the "
                "bowl, opening facing up."
            ),
        ),
        rubric=(
            "No purposeful contact with bowl or box",
            "Touches or moves the bowl or the box deliberately",
            "Bowl lifted and held clear of the table",
            "Box lifted and tilted over the bowl (pour attempted)",
            "At least one paper clip in the bowl, bowl and box released",
        ),
        report_slug="paperclip",
    ),
    TaskSpec(
        key="ruler_handover",
        title="Hand a ruler between arms, cup to cup",
        instruction=(
            "Transfer the ruler from the left cup to the right cup, but you must hand "
            "it over to the other arm's gripper in mid-air."
        ),
        objects=(
            "two paper cups (about 12 oz)",
            "one clear plastic 12 inch (30 cm) ruler",
        ),
        setup=(
            (
                "Stand one cup near the left arm and one near the right arm, at the "
                "same distance from the arm bases, so the ruler cannot be moved without "
                "a handover."
            ),
            "Stand the ruler in the left cup, leaning toward the far edge of the bench.",
            "Leave the right cup empty.",
        ),
        rubric=(
            "No purposeful contact with the ruler",
            "Touches or moves the ruler deliberately",
            "Ruler lifted clear of the left cup in one gripper",
            "Ruler held by the other gripper after a mid-air handover",
            "Ruler standing in the right cup and released",
        ),
        report_slug="ruler",
    ),
)

SPEC_BY_KEY: dict[str, TaskSpec] = {spec.key: spec for spec in SPECS}

RUBRIC_PRINCIPLES: tuple[str, ...] = (
    (
        "0 - nothing purposeful, 1 - deliberate contact with the target object(s), 2 - "
        "a secure grasp, 3 - the task's core manipulation achieved, 4 - the instruction "
        "fully satisfied."
    ),
    (
        "Every stage is a precondition of the next, and is a state that persists long "
        "enough to be judged from the video."
    ),
    (
        "A completed trial means stage 4, completion rate is the share of trials at "
        "stage 4. Mean stage summarises partial progress."
    ),
)
