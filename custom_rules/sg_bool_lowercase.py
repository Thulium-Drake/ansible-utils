"""Rule: Booleans must be lowercase true/false."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

_KV_RE = re.compile(r"^\s*[\w.-]+\s*:\s*(.+)$")
_BAD_BOOLS = re.compile(
    r"^(yes|no|Yes|No|YES|NO|True|False|TRUE|FALSE|on|off|On|Off|ON|OFF)$"
)


class BoolLowercaseRule(AnsibleLintRule):
    """Booleans must be lowercase true/false."""

    id = "sg-bool-lowercase"
    description = (
        "Per the project styleguide, boolean values must be 'true' or 'false', "
        "not 'yes', 'no', 'True', 'False', 'on', 'off', etc."
    )
    severity = "HIGH"
    tags = ["styleguide", "formatting"]
    version_changed = "1.0.0"

    def match(self, line: str) -> bool | str:
        stripped = line.rstrip()
        if stripped.lstrip().startswith("#"):
            return False

        m = _KV_RE.match(stripped)
        if not m:
            return False

        val = m.group(1).strip()
        # Remove inline comments
        if " #" in val:
            val = val[: val.index(" #")].strip()

        # Skip quoted values — they're strings, not booleans
        if (val.startswith("'") and val.endswith("'")) or (
            val.startswith('"') and val.endswith('"')
        ):
            return False

        if _BAD_BOOLS.match(val):
            return f"Use 'true' or 'false' instead of '{val}' for booleans."

        return False
