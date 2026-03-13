"""Rule: Task and play names must be quoted strings."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

# Matches: `- name: some value` or `  name: some value`
_NAME_LINE_RE = re.compile(r"^(\s*-?\s*)name\s*:\s*(.+)$")


class QuotedNameRule(AnsibleLintRule):
    """Task and play names must be quoted strings."""

    id = "sg-quoted-name"
    description = (
        "Per the project styleguide, task and play names are strings and "
        "should be quoted (single or double quotes)."
    )
    severity = "MEDIUM"
    tags = ["styleguide", "formatting"]
    version_changed = "1.0.0"

    def match(self, line: str) -> bool | str:
        m = _NAME_LINE_RE.match(line)
        if not m:
            return False

        val = m.group(2).strip()
        if not val:
            return False

        # Already quoted — OK
        if (val.startswith("'") and val.endswith("'")) or (
            val.startswith('"') and val.endswith('"')
        ):
            return False

        return f"Task/play name should be quoted: {val}"
