"""Rule: Bare variables in boolean context should use '| bool' filter."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

_KV_RE = re.compile(r"^\s*(when|changed_when|failed_when)\s*:\s*(.+)$")
_BARE_VAR_RE = re.compile(r"^[a-zA-Z_][\w.]*$")

# Known boolean properties that don't need | bool
_BOOL_PROPERTIES = frozenset({
    "changed", "failed", "skipped", "unreachable", "rc",
})


class BoolFilterRule(AnsibleLintRule):
    """Bare variables in boolean context should use the '| bool' filter."""

    id = "sg-bool-filter"
    description = (
        "Per the project styleguide, to ensure boolean values are processed "
        "correctly, pipe bare variables through the 'bool' filter in "
        "when/changed_when/failed_when conditions."
    )
    severity = "LOW"
    tags = ["styleguide", "idiom"]
    version_changed = "1.0.0"

    def match(self, line: str) -> bool | str:
        stripped = line.rstrip()
        if stripped.lstrip().startswith("#"):
            return False

        m = _KV_RE.match(stripped)
        if not m:
            return False

        val = m.group(2).strip()
        # Remove inline comments
        if " #" in val:
            val = val[: val.index(" #")].strip()

        if not val or val in ("true", "false"):
            return False

        # Dotted access ending in a known boolean property — already boolean
        if "." in val:
            prop = val.rsplit(".", 1)[1]
            if prop in _BOOL_PROPERTIES:
                return False

        # Only flag bare variable references
        if not _BARE_VAR_RE.match(val):
            return False

        return (
            f"Bare variable '{val}' in boolean context — "
            "consider using '| bool' filter."
        )
