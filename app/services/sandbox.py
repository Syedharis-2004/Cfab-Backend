"""
Sandbox execution service (MOCK LOCAL VERSION).

WARNING: This version executes user-submitted code directly on the host machine using subprocess.
It is INSECURE and intended ONLY for local testing when Docker is not available.
"""

import subprocess
import tempfile
import os
import shutil
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10  # wall-clock execution timeout

def _build_runner_script(code: str, stdin_input: str) -> str:
    """
    Wrap the user's code so that:
      1. stdin is redirected from a string (the test-case input).
      2. stdout is captured and printed normally.
    """
    escaped_input = stdin_input.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_code = code.replace("\\", "\\\\").replace('"', '\\"')

    runner = f'''
import sys
import io

_INPUT = "{escaped_input}"
sys.stdin = io.StringIO(_INPUT)

# ---- User code begins ----
exec("""{escaped_code}""")
# ---- User code ends ----
'''
    return runner


def run_code_in_sandbox(code: str, stdin_input: str) -> Tuple[bool, str, str]:
    """
    Execute *code* locally using subprocess instead of Docker.

    Returns:
        (success: bool, stdout: str, stderr: str)
    """
    temp_dir = tempfile.mkdtemp(prefix="mock_sandbox_")
    try:
        runner_path = os.path.join(temp_dir, "solution.py")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(_build_runner_script(code, stdin_input))

        # Run locally using standard Python
        result = subprocess.run(
            ["python", runner_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        success = result.returncode == 0
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if not success:
            logger.warning("Local execution exited with error: %s", stderr)
            
        return success, stdout, stderr

    except subprocess.TimeoutExpired as exc:
        stderr = f"Execution timed out after {TIMEOUT_SECONDS} seconds."
        logger.warning(stderr)
        return False, "", stderr

    except Exception as exc:
        logger.error("Local execution failed: %s", exc)
        return False, "", str(exc)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def evaluate_code(code: str, test_cases: list) -> dict:
    """
    Run *code* against every test case and return aggregate results.
    """
    total = len(test_cases)
    passed = 0
    last_error = None

    for tc in test_cases:
        success, stdout, stderr = run_code_in_sandbox(code, tc["input"])

        if not success:
            last_error = stderr or "Runtime error"
            continue

        expected = tc["expected_output"].strip()
        actual = stdout.strip()

        if actual == expected:
            passed += 1
        else:
            logger.debug("Test case failed. Expected: %r  Got: %r", expected, actual)

    score = int((passed / total) * 100) if total > 0 else 0

    return {
        "passed": passed,
        "total": total,
        "score": score,
        "error_message": last_error if passed < total else None,
    }
