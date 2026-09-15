"""Local Python Code Execution Sandbox & Chart Generator."""
import os
import sys
import time
import subprocess
import tempfile
from typing import Dict, Any

GENERATED_DIR = os.path.abspath("static/generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

def execute_python_code(code: str, timeout: int = 20) -> Dict[str, Any]:
    """
    Execute Python code locally in a subprocess and capture stdout, stderr, and matplotlib plots.
    """
    timestamp = int(time.time() * 1000)
    plot_filename = f"plot_{timestamp}.png"
    plot_path = os.path.join(GENERATED_DIR, plot_filename)

    # Prepend matplotlib headless setup and auto-figure capture
    wrapper_code = f"""
import os
import sys

# Ensure headless matplotlib
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_agent'
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    pass

# User Code
{code}

# Auto-save plot if figures were created
try:
    if 'plt' in locals() and plt.get_fignums():
        plt.tight_layout()
        plt.savefig('{plot_path}', dpi=120)
        plt.close('all')
        print(f"__PLOT_SAVED__:{plot_filename}")
except Exception as e:
    pass
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", wrapper_code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.abspath(".")
        )

        stdout = result.stdout
        stderr = result.stderr
        image_url = None

        if "__PLOT_SAVED__:" in stdout:
            parts = stdout.split("__PLOT_SAVED__:")
            stdout = parts[0].strip()
            saved_file = parts[1].strip()
            image_url = f"/generated/{saved_file}"
        elif os.path.exists(plot_path):
            image_url = f"/generated/{plot_filename}"

        return {
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "image_url": image_url,
            "exit_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "image_url": None,
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "image_url": None,
            "exit_code": 1
        }
