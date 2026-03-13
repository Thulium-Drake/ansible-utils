"""Rule: Jinja2 variables ({{ }}) must be wrapped in double quotes."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

_KV_RE = re.compile(r"^\s*[\w.-]+\s*:\s*(.+)$")
_BLOCK_SCALAR_RE = re.compile(r"^\s*[\w.-]+\s*:\s*[|>][+-]?\s*(#.*)?$")
_JINJA_VAR_RE = re.compile(r"\{\{.*?\}\}")


class JinjaDoubleQuotesRule(AnsibleLintRule):
    """Jinja2 variables must be wrapped in double quotes, not single."""

    id = "sg-jinja-double-quotes"
    description = (
        "Per the project styleguide, when using {{ variables }}, the value "
        "must be quoted with double quotes."
    )
    severity = "HIGH"
    tags = ["styleguide", "formatting"]
    version_changed = "1.0.0"

    def matchlines(self, file: Lintable) -> list[MatchError]:
        results: list[MatchError] = []
        in_block_scalar = False
        block_indent: int | None = None

        for line_num, line in enumerate(file.content.splitlines(), start=1):
            stripped = line.rstrip()

            # Track block scalar context
            if _BLOCK_SCALAR_RE.match(stripped):
                in_block_scalar = True
                block_indent = None
                continue

            if in_block_scalar:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else -1
                if current_indent == -1:
                    # blank line inside block scalar — keep going
                    continue
                if block_indent is None:
                    block_indent = current_indent
                if current_indent >= block_indent:
                    continue  # still inside block scalar
                # Dedented — left the block scalar
                in_block_scalar = False
                block_indent = None

            msg = self._check_line(stripped)
            if msg:
                results.append(
                    self.create_matcherror(
                        message=msg,
                        lineno=line_num,
                        filename=file,
                    )
                )
        return results

    @staticmethod
    def _check_line(stripped: str) -> str | bool:
        if stripped.lstrip().startswith("#") or "{{" not in stripped:
            return False

        m = _KV_RE.match(stripped)
        if not m:
            return False

        val = m.group(1).strip()
        # Remove inline comments
        if " #" in val:
            val = val[: val.index(" #")].strip()

        if not _JINJA_VAR_RE.search(val):
            return False

        # Already in double quotes — OK
        if val.startswith('"') and val.endswith('"'):
            return False

        # In single quotes — wrong
        if val.startswith("'") and val.endswith("'"):
            return "Jinja2 variables must be in double quotes, not single quotes."

        # Completely unquoted
        if not val.startswith('"'):
            return "Jinja2 variables ({{ }}) must be wrapped in double quotes."

        return False
