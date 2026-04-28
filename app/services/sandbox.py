import docker
import tempfile
import os
import shutil
import logging
import io
from typing import Tuple

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5
MEMORY_LIMIT = "128m"
CPU_QUOTA = 50000  # 50% of 1 CPU
SANDBOX_IMAGE = "python-sandbox:latest"

_client = None

def get_docker_client():
    # Docker is not available in Vercel serverless environment
    if os.getenv("VERCEL"):
        logger.warning("Running on Vercel: Docker sandbox is disabled.")
        return None

    global _client
    if _client is None:
        # Try different connection methods
        # 1. Standard Unix socket (common in Linux containers)
        # 2. Environment variables
        # 3. Windows Named Pipe
        for base_url in [None, 'unix:///var/run/docker.sock', 'npipe:////./pipe/docker_engine']:
            try:
                if base_url:
                    c = docker.DockerClient(base_url=base_url)
                else:
                    c = docker.from_env()
                c.ping()
                _client = c
                break
            except Exception:
                continue
        
        if _client is None:
            logger.error("Could not connect to Docker daemon using any method.")
    else:
        try:
            _client.ping()
        except Exception:
            _client = None
            return get_docker_client()
    return _client

def run_code_in_sandbox(code: str, stdin_input: str, function_name: str = None) -> Tuple[bool, str, str]:
    """
    Execute *code* inside a secure Docker container.
    If function_name is provided, it wraps the code to call that specific function.
    """
    client = get_docker_client()
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

        # Run container (create but don't start yet so we can put files)
        container = client.containers.create(
            image=SANDBOX_IMAGE,
            command=cmd,
            working_dir='/home/sandboxuser',
            mem_limit=MEMORY_LIMIT,
            cpu_quota=CPU_QUOTA,
            network_disabled=True,
            user=0 # Run as root to ensure we can write to /home/sandboxuser if needed
        )

        # Create tarball of the temp directory
        import tarfile
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                tar.add(filepath, arcname=filename)
        tar_stream.seek(0)
        
        # Put files in container
        container.put_archive('/home/sandboxuser', tar_stream)
        
        # Start container
        container.start()

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
