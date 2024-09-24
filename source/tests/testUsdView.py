# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import tempfile
import unittest

# Internal imports
import utils.shell


class UsdViewTestCase(unittest.TestCase):
    def testUsdView(self):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
            return_code, output = utils.shell.run_shell_script("run", "createStage", "-p", stagePath)
            self.assertEqual(return_code, 0, output)

            # This path to `usdview_gui` must match what's in usdview.bat|sh to be a valid test
            # repo_test hangs on Windows when `usdview.bat` is used here
            return_code, output = utils.shell.run_shell_script(
                "_build/target-deps/usd/release/scripts/usdview_gui", "--quitAfterStartup", "--norender", stagePath
            )
            self.assertEqual(return_code, 0, output)
