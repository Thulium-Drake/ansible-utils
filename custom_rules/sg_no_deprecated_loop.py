"""Rule: Use 'loop' instead of deprecated with_* directives."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task

_DEPRECATED_LOOPS = frozenset({
    "with_items",
    "with_list",
    "with_dict",
    "with_fileglob",
    "with_filetree",
    "with_first_found",
    "with_flattened",
    "with_indexed_items",
    "with_ini",
    "with_inventory_hostnames",
    "with_lines",
    "with_nested",
    "with_random_choice",
    "with_sequence",
    "with_subelements",
    "with_together",
})


class NoDeprecatedLoopRule(AnsibleLintRule):
    """Use 'loop' instead of deprecated with_* directives."""

    id = "sg-no-deprecated-loop"
    description = (
        "Per the project styleguide, use the 'loop' keyword instead of "
        "deprecated with_items, with_dict, with_list, etc."
    )
    severity = "HIGH"
    tags = ["styleguide", "deprecations"]
    version_changed = "1.0.0"
    needs_raw_task = True

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        raw = task.get("__raw_task__", task.raw_task)
        for key in raw:
            if key in _DEPRECATED_LOOPS:
                return f"Use 'loop' instead of deprecated '{key}'."
        return False
