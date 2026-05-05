#!/usr/bin/env python3
"""DataBridge one-time setup — cross-platform (Windows, macOS, Linux).

Creates an isolated Python environment at ~/.databridge/venv with the
packages DataBridge skill scripts need (pymongo + pandas), writes the
user's MongoDB URI to ~/.databridge.env, pings the server, and marks
state.json as setup_complete.

Safe to re-run: existing venv is reused, existing URI is the default
prompt value, state.json is refreshed.
"""

import os
import subprocess
import sys
from pathlib import Path

STATE_DIR = Path.home() / ".databridge"
ENV_FILE = Path.home() / ".databridge.env"
VENV_DIR = STATE_DIR / "venv"
DEFAULT_URI = "mongodb://localhost:27017/databridge"
SCRIPT_DIR = Path(__file__).resolve().parent

# Cross-platform venv Python executable path
_scripts = "Scripts" if sys.platform == "win32" else "bin"
_exe = "python.exe" if sys.platform == "win32" else "python"
VENV_PYTHON = VENV_DIR / _scripts / _exe


def _check_python_version() -> None:
    if sys.version_info < (3, 11):
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        sys.exit(f"error: need Python >= 3.11, found {ver}.")


def _create_venv() -> None:
    if not VENV_DIR.exists():
        print(f"Creating isolated environment at {VENV_DIR} ...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def _install_packages() -> None:
    print("Installing pymongo and pandas (quiet) ...")
    subprocess.run(
        [str(VENV_PYTHON), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [
            str(VENV_PYTHON), "-m", "pip", "install", "--quiet",
            "pymongo>=4.6", "pandas>=2.0",
        ],
        check=True,
    )


def _prompt_uri() -> str:
    existing = ""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("MONGO_URI="):
                existing = line[len("MONGO_URI="):].strip().strip('"').strip("'")
                break
    default = existing or DEFAULT_URI
    try:
        answer = input(f"MongoDB URI [{default}]: ").strip()
    except EOFError:
        answer = ""
    return answer or default


def _ping_mongo(uri: str) -> None:
    print("Verifying connection ...")
    ping_code = (
        "import os, sys\n"
        "from pymongo import MongoClient\n"
        "try:\n"
        "    MongoClient(os.environ['MONGO_URI'], serverSelectionTimeoutMS=5000)"
        ".admin.command('ping')\n"
        "except Exception as e:\n"
        "    print(f'ping failed: {e}', file=sys.stderr)\n"
        "    sys.exit(1)\n"
    )
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", ping_code],
        env={**os.environ, "MONGO_URI": uri},
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        sys.exit(
            f"error: could not reach MongoDB at {uri}.\n"
            "       Start the server (brew / docker / atlas) and re-run this script."
        )


def _write_env_file(uri: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(f"MONGO_URI={uri}\n", encoding="utf-8")
    # Restrict permissions on Unix (equivalent to umask 077)
    if sys.platform != "win32":
        os.chmod(ENV_FILE, 0o600)


def main() -> None:
    _check_python_version()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _create_venv()
    _install_packages()

    uri = _prompt_uri()
    _ping_mongo(uri)
    _write_env_file(uri)

    # Let doctor.py write the state file (single source of truth)
    subprocess.run([str(VENV_PYTHON), str(SCRIPT_DIR / "doctor.py")], check=True)

    print(f"""
DataBridge is ready.

State:      {STATE_DIR / "state.json"}
URI file:   {ENV_FILE}
venv:       {VENV_DIR}

Next steps:
  - To load a dataset, see its skill's scripts/SOURCE.md.
  - Run the venv Python directly: {VENV_PYTHON}
""")


if __name__ == "__main__":
    main()
