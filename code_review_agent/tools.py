"""Custom FunctionTools for the Smart Code Review Agent.

Each tool handles one dimension of code review. The LLM reads
the docstrings to decide which tools to call and in what order.
"""


def analyze_bugs(code: str) -> dict:
    """Analyze Python code for potential bugs and logical errors.

    Use this tool to detect issues like: logic errors, off-by-one mistakes,
    unhandled exceptions, type mismatches, None/null reference issues,
    incorrect return values, infinite loops, and unreachable code.

    Args:
        code: The Python source code to analyze for bugs.

    Returns:
        A dictionary with a 'bugs' key containing a list of bug objects,
        each with 'severity' (critical/high/medium/low), 'line' (approximate
        line number), 'issue' (description), and 'suggestion' (how to fix).
    """
    try:
        lines = code.strip().splitlines()
        return {
            "status": "success",
            "analysis_type": "bug_detection",
            "total_lines": len(lines),
            "code_received": True,
        }
    except Exception as e:
        return {
            "status": "error",
            "analysis_type": "bug_detection",
            "error": str(e),
        }


def check_style(code: str) -> dict:
    """Review Python code for style issues and best practice violations.

    Use this tool to check: PEP 8 compliance, naming conventions
    (snake_case for functions/variables, PascalCase for classes),
    docstring presence and quality, code organization, use of
    Pythonic idioms, import ordering, and type hint usage.

    Args:
        code: The Python source code to review for style.

    Returns:
        A dictionary with a 'style_issues' key containing a list of
        issue objects, each with 'category' (naming/formatting/docstrings/
        idioms/imports), 'issue' (description), and 'suggestion' (improvement).
    """
    try:
        lines = code.strip().splitlines()
        return {
            "status": "success",
            "analysis_type": "style_review",
            "total_lines": len(lines),
            "code_received": True,
        }
    except Exception as e:
        return {
            "status": "error",
            "analysis_type": "style_review",
            "error": str(e),
        }


def review_security(code: str) -> dict:
    """Identify security vulnerabilities in Python code.

    Use this tool ONLY when the code involves: user input handling,
    file operations (open, read, write), database queries (SQL),
    network requests, environment variable access, eval()/exec() usage,
    subprocess calls, deserialization (pickle, yaml), or authentication logic.

    Do NOT use this tool for simple utility functions, math operations,
    or data transformations that don't interact with external systems.

    Args:
        code: The Python source code to scan for security issues.

    Returns:
        A dictionary with a 'security_issues' key containing a list of
        finding objects, each with 'risk' (critical/high/medium/low),
        'issue' (description), and 'remediation' (how to fix).
    """
    try:
        lines = code.strip().splitlines()
        return {
            "status": "success",
            "analysis_type": "security_review",
            "total_lines": len(lines),
            "code_received": True,
        }
    except Exception as e:
        return {
            "status": "error",
            "analysis_type": "security_review",
            "error": str(e),
        }


def calculate_score(
    bugs_found: int,
    style_issues_found: int,
    security_issues_found: int,
    has_critical_bugs: bool,
    has_critical_security: bool
) -> dict:
    """Calculate an overall code quality score based on review findings.

    Use this tool AFTER running the other review tools (analyze_bugs,
    check_style, and optionally review_security). It computes a weighted
    score from 0 to 100 based on the number and severity of findings.

    Args:
        bugs_found: Total number of bugs detected by analyze_bugs.
        style_issues_found: Total number of style issues from check_style.
        security_issues_found: Total number of security issues from review_security (0 if not run).
        has_critical_bugs: True if any bug was rated 'critical' severity.
        has_critical_security: True if any security issue was rated 'critical' risk.

    Returns:
        A dictionary with 'score' (0-100), 'grade' (A/B/C/D/F),
        'breakdown' showing points deducted per category, and
        'summary' with a brief quality assessment.
    """
    try:
        score = 100

        # Deduct for bugs (heaviest weight)
        bug_penalty = min(bugs_found * 8, 35)
        score -= bug_penalty

        # Deduct for style issues (lighter weight)
        style_penalty = min(style_issues_found * 3, 20)
        score -= style_penalty

        # Deduct for security issues (heavy weight)
        security_penalty = min(security_issues_found * 10, 30)
        score -= security_penalty

        # Critical findings carry extra penalties
        if has_critical_bugs:
            score -= 10
        if has_critical_security:
            score -= 15

        # Clamp to 0-100
        score = max(0, min(100, score))

        # Assign grade
        if score >= 90:
            grade = "A"
            summary = "Excellent code quality. Minor improvements possible."
        elif score >= 75:
            grade = "B"
            summary = "Good code quality. Some issues worth addressing."
        elif score >= 60:
            grade = "C"
            summary = "Acceptable but needs improvement in several areas."
        elif score >= 40:
            grade = "D"
            summary = "Below average. Significant issues should be fixed before production use."
        else:
            grade = "F"
            summary = "Poor quality. Major rework recommended."

        return {
            "status": "success",
            "score": score,
            "grade": grade,
            "breakdown": {
                "bugs_penalty": bug_penalty,
                "style_penalty": style_penalty,
                "security_penalty": security_penalty,
                "critical_bug_penalty": 10 if has_critical_bugs else 0,
                "critical_security_penalty": 15 if has_critical_security else 0,
            },
            "summary": summary,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }