import os
import unittest
from pathlib import Path

import pytest

from converter.motionarea import MotionArea
from pmac_motorhome._version import __version__


class TestMotionArea(unittest.TestCase):
    @pytest.mark.skipif(
        os.environ.get("GITHUB_ACTIONS") == "true"
        or os.environ.get("REMOTE_CONTAINERS") == "true",
        reason="conversion tests are not relevant outside DLS",
    )
    def test_shebang_looks_as_expected(self):
        # Arrange
        expected_shebang = (
            "#!/bin/env /dls_sw/prod/python3/RHEL7-x86_64/pmac_motorhome/"
            + __version__
            + "/lightweight-venv/bin/python3"
        )
        motionarea = MotionArea(Path("/tmp"))
        # Act
        content = motionarea.get_shebang()
        # Assert
        self.assertEqual(content, expected_shebang)
