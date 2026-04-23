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

def run_code_in_sandbox(code: str, stdin_input: str) -> Tuple[bool, str, str]:
    """
    Execute *code* inside a secure Docker container.
    """
    if client is None:
        return False, "", "Docker service not available on host."

    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    try:
        # Write user code to a file
        solution_path = os.path.join(temp_dir, "solution.py")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Run container
        # We mount the directory and run python solution.py
        # We pass stdin via a separate mechanism or by piping it.
        # Since docker-py's 'run' with command is easier, we'll try to pipe stdin if possible.
        # However, a simpler way is to use a wrapper script inside the container or just exec.
        
        container = client.containers.run(
            image=SANDBOX_IMAGE,
            command=["python", "solution.py"],
            volumes={temp_dir: {'bind': '/home/sandboxuser', 'mode': 'ro'}},
            working_dir='/home/sandboxuser',
            mem_limit=MEMORY_LIMIT,
            cpu_quota=CPU_QUOTA,
            network_disabled=True,
            detach=True,
            stdin_open=True,
            # We don't use 'remove=True' here because we want to capture logs first
        )

        try:
            # Send input to stdin
            # Note: This is a bit tricky with docker-py's run.
            # A better way is to include a runner script.
            
            # For simplicity in this demo, we'll use a runner that reads from a file.
            # Let's write the input to a file too.
            input_path = os.path.join(temp_dir, "input.txt")
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(stdin_input)
            
            # Update command to read from input.txt
            # We'll re-create the container logic with this change.
            container.stop()
            container.remove()
            
            container = client.containers.run(
                image=SANDBOX_IMAGE,
                command=["sh", "-c", "python solution.py < input.txt"],
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
                container.kill()
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
