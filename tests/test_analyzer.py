from codebug_bot.analyzer import analyze_code


def test_missing_colon():
    code = "def f(x)\n    return x"
    result = analyze_code(code)
    kinds = [i["issue_type"] for i in result["issues"]]
    assert "missing_colon" in kinds


def test_missing_parenthesis():
    code = "print((1+2)"
    result = analyze_code(code)
    kinds = [i["issue_type"] for i in result["issues"]]
    assert "missing_parenthesis" in kinds or "syntax_error" in kinds
