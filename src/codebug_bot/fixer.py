from __future__ import annotations

from typing import Any

BLOCK_STARTERS = (
    "if",
    "elif",
    "else",
    "for",
    "while",
    "try",
    "except",
    "finally",
    "with",
    "def",
    "class",
    "match",
    "case",
)


def _ensure_trailing_colon(line: str) -> str:
    return line.rstrip() + ":"


def _close_parentheses_at_end(code: str) -> str:
    # naive balance-based closer
    open_count = code.count("(")
    close_count = code.count(")")
    missing = open_count - close_count
    if missing > 0:
        return code + (")" * missing)
    return code


def _balance_brackets(code: str) -> str:
    # conservative: no-op (hard to auto-fix safely)
    return code


def _try_fix_single_line_quote(line: str) -> str:
    # If odd number of ' or " on the line, try appending the same quote
    s = line
    if s.count("'") % 2 != 0:
        return s + "'"
    if s.count('"') % 2 != 0:
        return s + '"'
    return line


def apply_fixes(code: str, analysis: dict[str, Any]) -> str:
    lines = code.splitlines()
    issues = analysis.get("issues", [])
    fixed = lines[:]
    for issue in issues:
        t = issue.get("issue_type")
        ln = issue.get("line", 1)
        if t == "missing_colon" and 1 <= ln <= len(fixed):
            fixed[ln - 1] = _ensure_trailing_colon(fixed[ln - 1])
        elif t == "missing_parenthesis":
            return _close_parentheses_at_end("\n".join(fixed))
        elif t == "missing_quotation" and 1 <= ln <= len(fixed):
            fixed[ln - 1] = _try_fix_single_line_quote(fixed[ln - 1])
        elif t == "mismatched_bracket":
            # currently conservative
            return _balance_brackets("\n".join(fixed))
    return "\n".join(fixed)
