# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import sys
import tempfile
import unittest

import common.sysUtils
import utils.shell
from utils.ScopedEnvVar import ScopedEnvVar


class RunAllTestCase(unittest.TestCase):

    def testRunAllCpp(self):
        if "-e" in sys.argv and "keep" in sys.argv:
            stagePath = common.sysUtils.getDefaultStagePath(".cpp.usda")
            print(f"\nStage output to {stagePath}")
            return_code, output = utils.shell.run_shell_script("run", "all", "-p", stagePath)
            self.assertEqual(return_code, 0, output)
        else:
            with tempfile.TemporaryDirectory() as tempDirStr:
                tempDir = pathlib.Path(tempDirStr)
                stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                return_code, output = utils.shell.run_shell_script("run", "all", "-p", stagePath)
                self.assertEqual(return_code, 0, output)

                # Check that the stage was created
                stagePathObj = pathlib.Path(stagePath)
                self.assertTrue(stagePathObj.exists(), f"Stage file {stagePathObj} does not exist")

    def testRunAllPython(self):
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            pySampleBaseDir = "source/python/"
            if "-e" in sys.argv and "keep" in sys.argv:
                stagePath = common.sysUtils.getDefaultStagePath(".python.usda")
                print(f"\nStage output to {stagePath}")
                return_code, output = utils.shell.run_shell_script("python", f"{pySampleBaseDir}all.py", "-p", stagePath)
                self.assertEqual(return_code, 0, output)
            else:
                with tempfile.TemporaryDirectory() as tempDirStr:
                    tempDir = pathlib.Path(tempDirStr)
                    stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                    return_code, output = utils.shell.run_shell_script("python", f"{pySampleBaseDir}all.py", "-p", stagePath)
                    self.assertEqual(return_code, 0, output)

                    # Check that the stage was created
                    stagePathObj = pathlib.Path(stagePath)
                    self.assertTrue(stagePathObj.exists(), f"Stage file {stagePathObj} does not exist")

    def testAllSamplesConsistency(self):
        samples = common.sysUtils.getAllSamples()

        # There are some extra files and directories in the source directories that are not samples
        sampleEntriesToIgnore = ["__pycache__", "all", "assetValidator", "common", "python", "tests", "usdTraverse"]
        samples.extend(sampleEntriesToIgnore)

        # Check that the samples are consistent with the directory names in the source directory
        sourceDir = pathlib.Path(__file__).parent.parent.parent / "source"
        for sampleDir in sourceDir.iterdir():
            if sampleDir.is_dir():
                sample = sampleDir.name
                if sample not in samples:
                    self.fail(f"Sample <{sample}> not found in allSamples.txt")

        pythonDir = pathlib.Path(__file__).parent.parent.parent / "source" / "python"
        for sampleFile in pythonDir.iterdir():
            if sampleFile.is_file():
                sample = sampleFile.stem
                if f"{sample}" not in samples:
                    self.fail(f"Sample <{sample}> not found in allSamples.txt")
