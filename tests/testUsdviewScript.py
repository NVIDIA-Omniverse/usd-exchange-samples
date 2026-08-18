# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import pathlib
import platform
import shutil
import subprocess
import tempfile
import unittest


class UsdviewScriptArgumentTestCase(unittest.TestCase):
    def test_arguments_with_spaces_are_forwarded_intact(self):
        if platform.system() == "Windows":
            self.skipTest("usdview.sh is not used on Windows")
        if not os.access("/bin/bash", os.X_OK):
            self.skipTest("bash interpreter not available")

        repoRoot = pathlib.Path(__file__).resolve().parent.parent.parent
        sourceScript = repoRoot / "usdview.sh"
        if not sourceScript.exists():
            self.skipTest("usdview.sh not found")

        with tempfile.TemporaryDirectory() as tmpStr:
            tmpDir = pathlib.Path(tmpStr)
            scriptPath = tmpDir / "usdview.sh"
            shutil.copy(sourceScript, scriptPath)
            scriptPath.chmod(0o755)

            fakeUsdview = (
                tmpDir
                / "_build"
                / "target-deps"
                / "usd"
                / "release"
                / "scripts"
                / "usdview_gui.sh"
            )
            fakeUsdview.parent.mkdir(parents=True, exist_ok=True)
            fakeUsdview.write_text(
                '#!/bin/bash\n'
                'printf "%s\\n" "$#"\n'
                'printf "%s\\n" "$@"\n'
            )
            fakeUsdview.chmod(0o755)

            fakeActivate = tmpDir / "_build" / "usdview_venv" / "bin" / "activate"
            fakeActivate.parent.mkdir(parents=True, exist_ok=True)
            fakeActivate.write_text("#!/bin/bash\n")
            fakeActivate.chmod(0o755)

            stageArg = "stage path with spaces.usda"
            result = subprocess.run(
                [str(scriptPath), "--norender", stageArg],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            lines = result.stdout.strip().splitlines()
            self.assertEqual(lines[0], "2", f"unexpected arg count: {lines!r}")
            self.assertEqual(lines[1], "--norender")
            self.assertEqual(lines[2], stageArg)
