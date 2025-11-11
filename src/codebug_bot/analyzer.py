from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any

BLOCK_KEYWORDS = {
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
}


@dataclass
class Issue:
    issue_type: str
    line: int
    col: int | None
    message: str
    confidence: float


def _line_requires_colon(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    # e.g., "if x" or "def f(x)"
    head = stripped.split()[0]
    return head in BLOCK_KEYWORDS and not stripped.endswith(":")


def _count_unbalanced_pairs(code: str) -> dict[str, int]:
    pairs = {"()": 0, "[]": 0, "{}": 0}
    for ch in code:
        if ch == "(":
            pairs["()"] += 1
        elif ch == ")":
            pairs["()"] -= 1
        elif ch == "[":
            pairs["[]"] += 1
        elif ch == "]":
            pairs["[]"] -= 1
        elif ch == "{":
            pairs["{}"] += 1
        elif ch == "}":
            pairs["{}"] -= 1
    return pairs


def _quote_imbalance(line: str) -> bool:
    # Rough: ignore escaped quotes
    s = re.sub(r"\\\"", "", line)
    s = re.sub(r"\\'", "", s)
    return (s.count('"') % 2 != 0) or (s.count("'") % 2 != 0)


def analyze_code(code: str) -> dict[str, Any]:
    lines = code.splitlines()
    # First, try parsing: if it fails, capture error
    try:
        ast.parse(code)
        parse_ok = True
        syntax_error = None
    except SyntaxError as e:
        parse_ok = False
        syntax_error = e

    issues: list[Issue] = []

    if not parse_ok and syntax_error is not None:
        err_line = syntax_error.lineno or 1
        err_col = syntax_error.offset or None
        msg = syntax_error.msg.lower()

        # Heuristic classification
        if "expected ':'" in msg or _line_requires_colon(
            lines[err_line - 1] if 0 < err_line <= len(lines) else ""
        ):
            issues.append(
                Issue(
                    "missing_colon",
                    err_line,
                    err_col,
                    "Possível ':' ausente ao fim do bloco.",
                    0.95,
                )
            )
        elif "unexpected eof" in msg or "was never closed" in msg:
            pairs = _count_unbalanced_pairs(code)
            if pairs["()"] > 0:
                issues.append(
                    Issue(
                        "missing_parenthesis",
                        len(lines),
                        None,
                        "Parêntese de fechamento possivelmente ausente.",
                        0.9,
                    )
                )
            elif pairs["[]"] != 0 or pairs["{}"] != 0:
                issues.append(
                    Issue(
                        "mismatched_bracket",
                        err_line,
                        err_col,
                        "Colchetes/chaves desequilibrados.",
                        0.8,
                    )
                )
            else:
                # fallback
                issues.append(
                    Issue(
                        "syntax_error",
                        err_line,
                        err_col,
                        f"Erro de sintaxe: {syntax_error.msg}",
                        0.6,
                    )
                )
        elif "invalid syntax" in msg:
            # Try quotes on the error line
            candidate_line = lines[err_line - 1] if 0 < err_line <= len(lines) else ""
            if _quote_imbalance(candidate_line):
                issues.append(
                    Issue(
                        "missing_quotation",
                        err_line,
                        err_col,
                        "Aspas possivelmente faltando/fechamento incorreto.",
                        0.85,
                    )
                )
            else:
                pairs = _count_unbalanced_pairs(code)
                if pairs["()"] != 0:
                    issues.append(
                        Issue(
                            "missing_parenthesis",
                            err_line,
                            err_col,
                            "Parênteses desequilibrados.",
                            0.8,
                        )
                    )
                elif pairs["[]"] != 0 or pairs["{}"] != 0:
                    issues.append(
                        Issue(
                            "mismatched_bracket",
                            err_line,
                            err_col,
                            "Colchetes/chaves desequilibrados.",
                            0.8,
                        )
                    )
                else:
                    issues.append(
                        Issue(
                            "syntax_error",
                            err_line,
                            err_col,
                            f"Erro de sintaxe: {syntax_error.msg}",
                            0.6,
                        )
                    )
        else:
            issues.append(
                Issue(
                    "syntax_error",
                    err_line,
                    err_col,
                    f"Erro de sintaxe: {syntax_error.msg}",
                    0.6,
                )
            )
    else:
        # Parse OK. Still run lightweight checks: quotes / brackets
        for i, ln in enumerate(lines, start=1):
            if _line_requires_colon(ln):
                issues.append(
                    Issue(
                        "missing_colon",
                        i,
                        None,
                        "Linha de bloco sem ':' ao final.",
                        0.6,
                    )
                )
        pairs = _count_unbalanced_pairs(code)
        if any(v != 0 for v in pairs.values()):
            issues.append(
                Issue(
                    "mismatched_bracket",
                    1,
                    None,
                    "Parênteses/colchetes/chaves desequilibrados.",
                    0.5,
                )
            )
        for i, ln in enumerate(lines, start=1):
            if _quote_imbalance(ln):
                issues.append(
                    Issue(
                        "missing_quotation",
                        i,
                        None,
                        "Aspas possivelmente faltando/fechamento incorreto.",
                        0.5,
                    )
                )

    return {
        "ok": parse_ok,
        "issues": [issue.__dict__ for issue in issues],
    }
