from __future__ import annotations
from typing import Dict, Any
from .analyzer import analyze_code
from .fixer import apply_fixes

def chat_process(user_code: str, apply_fix: bool = True) -> Dict[str, Any]:
    analysis = analyze_code(user_code)
    fixed_code = None
    if apply_fix:
        try:
            fixed_code = apply_fixes(user_code, analysis)
        except Exception:
            fixed_code = None
    return {
        "analysis": analysis,
        "fixed_code": fixed_code
    }
