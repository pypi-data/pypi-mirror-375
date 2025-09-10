import subprocess
import sys

from pmac_motorhome import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "pmac_motorhome", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
