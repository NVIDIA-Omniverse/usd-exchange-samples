# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import difflib
import filecmp
import pathlib
import tempfile
import unittest

# Internal imports
import utils.shell


class BaseTestCase(unittest.TestCase):
    def compareTextOutput(self, cppName, pythonScript):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            stagePaths = [pathlib.Path(tempDir / "test_stage_cpp.usda").as_posix(), pathlib.Path(tempDir / "test_stage_python.usda").as_posix()]
            return_code, output = utils.shell.run_shell_script("run", cppName, "-p", stagePaths[0])
            self.assertEqual(return_code, 0, output)
            return_code, output = utils.shell.run_shell_script("python", pythonScript, "-p", stagePaths[1])
            self.assertEqual(return_code, 0, output)

            def printUsdFiles(files):
                with open(files[0]) as cppFile:
                    with open(files[1]) as pyFile:
                        cppLines = cppFile.readlines()
                        pyLines = pyFile.readlines()
                        diffLines = difflib.unified_diff(cppLines, pyLines, fromfile=files[0], tofile=files[1])
                        return "".join(diffLines)

            filecmp.clear_cache()
            self.assertTrue(filecmp.cmp(stagePaths[0], stagePaths[1]), msg=printUsdFiles(stagePaths))

    def runAssetValidator(self, stagePath):
        return_code, output = utils.shell.run_shell_script("omni_asset_validator", stagePath)
        self.assertEqual(return_code, 0, output)
        for line in output.splitlines():
            if line.lower().startswith("warning") or line.lower().startswith("error") or line.lower().startswith("fatal"):
                self.fail(msg=line)
