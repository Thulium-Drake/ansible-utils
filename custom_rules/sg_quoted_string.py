"""Rule: String values should be quoted."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable

_KV_RE = re.compile(r"^\s*([\w.-]+)\s*:\s*(.+)$")

# Keys whose values are typically not plain strings (expressions, booleans, etc.)
_NON_STRING_KEYS = frozenset({
    "when", "changed_when", "failed_when", "until", "retries",
    "delay", "register", "become", "gather_facts", "ignore_errors",
    "ignore_unreachable", "check_mode", "diff", "no_log", "that",
    "run_once", "delegate_to", "delegate_facts", "any_errors_fatal",
    "serial", "max_fail_percentage", "throttle", "order",
    "tags", "notify", "listen", "hosts", "connection",
    "strategy", "collections", "module_defaults", "vars",
    "environment", "block", "rescue", "always",
    "loop", "loop_control", "loop_var",
    "async", "poll", "timeout", "var",
})

# Patterns indicating the value is an expression, not a plain string
_EXPRESSION_RE = re.compile(
    r"""
      ^not\s                  # negation
    | \s==\s | \s!=\s         # comparison
    | \s>=\s | \s<=\s         # comparison
    | \s>\s  | \s<\s          # comparison
    | \sis\s                  # identity test
    | \sin\s                  # membership
    | \sand\s | \sor\s        # logical
    | \s\|\s                  # filter pipe
    | ^\w+\.\w+              # dotted reference
    """,
    re.VERBOSE,
)


def _looks_like_expression(val: str) -> bool:
    if re.match(r"^[a-zA-Z_]\w*$", val):
        return True
    return bool(_EXPRESSION_RE.search(val))


class QuotedStringRule(AnsibleLintRule):
    """String values should be quoted."""

    id = "sg-quoted-string"
    description = (
        "Per the project styleguide, string values should be quoted. "
        "Use single quotes for plain strings, double quotes when "
        "the string contains Jinja2 variables."
    )
    severity = "LOW"
    tags = ["styleguide", "formatting"]
    version_changed = "1.0.0"

    def match(self, line: str) -> bool | str:
        stripped = line.rstrip()
        if stripped.lstrip().startswith("#") or not stripped.strip():
            return False

        m = _KV_RE.match(stripped)
        if not m:
            return False

        key = m.group(1)
        val = m.group(2).strip()

        # Block scalar
        if val.startswith("|") or val.startswith(">"):
            return False

        # Remove inline comments
        if " #" in val:
            val = val[: val.index(" #")].strip()

        if key in _NON_STRING_KEYS:
            return False

        # Skip empty, booleans, numbers, null, jinja (separate rule)
        if not val or val in ("true", "false", "null", "~"):
            return False
        if re.match(r"^-?\d+\.?\d*$", val):
            return False
        # Already quoted
        if (val.startswith("'") and val.endswith("'")) or (
            val.startswith('"') and val.endswith('"')
        ):
            return False
        # List/dict starts
        if val.startswith("[") or val.startswith("{"):
            return False
        # Jinja — handled by sg-jinja-double-quotes
        if "{{" in val:
            return False
        # Expressions should be unquoted per styleguide
        if _looks_like_expression(val):
            return False

        return f"String value should be quoted: {val}"
