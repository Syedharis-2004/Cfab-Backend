import docker
import tempfile
import os
import shutil
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5
MEMORY_LIMIT = "128m"
CPU_QUOTA = 50000  # 50% of 1 CPU
SANDBOX_IMAGE = "python-sandbox:latest"

try:
    client = docker.from_env()
except Exception as e:
    logger.warning(f"Docker not available: {e}. Coding sandbox will fail if Docker is not started.")
    client = None

def run_code_in_sandbox(code: str, stdin_input: str, function_name: str = None) -> Tuple[bool, str, str]:
    """
    Execute *code* inside a secure Docker container.
    If function_name is provided, it wraps the code to call that specific function.
    """
    if client is None:
        return False, "", "Docker service not available on host."

    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    try:
        # Write user code to a file
        solution_path = os.path.join(temp_dir, "solution.py")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Create a runner script that calls the specific function if needed
        if function_name:
            runner_path = os.path.join(temp_dir, "runner.py")
            with open(runner_path, "w", encoding="utf-8") as f:
                f.write(f"""
import solution
import sys
import json

try:
    # Read input from stdin
    raw_input = sys.stdin.read().strip()
    
    # Try to parse as JSON if it looks like it, otherwise pass as string
    try:
        if (raw_input.startswith('[') and raw_input.endswith(']')) or (raw_input.startswith('{{') and raw_input.endswith('}}')):
            val = json.loads(raw_input)
        else:
            val = raw_input
    except:
        val = raw_input

    # Call the function
    result = solution.{function_name}(val)
    
    # Output the result
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
""")
            cmd = ["sh", "-c", "python runner.py < input.txt"]
        else:
            cmd = ["sh", "-c", "python solution.py < input.txt"]

        # Write input to a file
        input_path = os.path.join(temp_dir, "input.txt")
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(stdin_input)

        # Run container
        container = client.containers.run(
            image=SANDBOX_IMAGE,
            command=cmd,
            volumes={temp_dir: {'bind': '/home/sandboxuser', 'mode': 'ro'}},
            working_dir='/home/sandboxuser',
            mem_limit=MEMORY_LIMIT,
            cpu_quota=CPU_QUOTA,
            network_disabled=True,
            detach=True
        )

        # Wait for completion with timeout
        try:
            exit_status = container.wait(timeout=TIMEOUT_SECONDS)
            success = exit_status['StatusCode'] == 0
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8").strip()
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8").strip()
            return success, stdout, stderr
        except Exception as e:
            try:
                container.kill()
            except:
                pass
            return False, "", f"Execution timed out or failed: {str(e)}"
        finally:
            try:
                container.remove(force=True)
            except:
                pass

    except Exception as exc:
        logger.error("Sandbox execution failed: %s", exc)
        return False, "", str(exc)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def evaluate_code(code: str, test_cases: list, function_name: str = None) -> dict:
    """
    Run *code* against every test case and return aggregate results.
    """
    total = len(test_cases)
    passed = 0
    last_error = None

    for tc in test_cases:
        success, stdout, stderr = run_code_in_sandbox(code, tc["input"], function_name)

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
