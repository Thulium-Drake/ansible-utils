"""Rule: loop should be accompanied by loop_control with loop_var."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task


class LoopControlRule(AnsibleLintRule):
    """Tasks using 'loop' should have loop_control with loop_var."""

    id = "sg-loop-control"
    description = (
        "Per the project styleguide, when using 'loop', include "
        "'loop_control' with 'loop_var' to prevent variable collisions."
    )
    severity = "MEDIUM"
    tags = ["styleguide", "idiom"]
    version_changed = "1.0.0"
    needs_raw_task = True

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        raw = task.get("__raw_task__", task.raw_task)

        if "loop" not in raw:
            return False

        loop_control = raw.get("loop_control")
        if not isinstance(loop_control, dict) or "loop_var" not in loop_control:
            return (
                "'loop' without 'loop_control' / 'loop_var'. "
                "Add loop_control to prevent variable collisions."
            )

        return False
