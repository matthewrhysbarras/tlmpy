import shutil
import subprocess
import sys

from tlmpy._version import __version__


def test_python_module_version():
    completed = subprocess.run(
        [sys.executable, "-m", "tlmpy", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert __version__ in completed.stdout


def test_python_module_info():
    completed = subprocess.run(
        [sys.executable, "-m", "tlmpy", "info"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert __version__ in completed.stdout
    assert "numpy" in completed.stdout.lower()
    assert "cupy" in completed.stdout.lower()


def test_console_script_info_when_available():
    script = shutil.which("tlmpy")
    if script is None:
        return

    completed = subprocess.run(
        [script, "info"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert __version__ in completed.stdout
    assert "numpy" in completed.stdout.lower()
    assert "cupy" in completed.stdout.lower()
