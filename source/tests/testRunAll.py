# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import sys
import tempfile
import unittest

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import utils.shell
from utils.ScopedEnvVar import ScopedEnvVar


class RunAllTestCase(unittest.TestCase):

    def _getSamples(self) -> list[str]:
        # Read samples from allSamples.txt
        # The test file is in source/tests/, so we need to go up two levels to reach the root
        allSamplesPath = pathlib.Path(__file__).parent.parent.parent / "allSamples.txt"
        samples = []
        try:
            with open(allSamplesPath, "r") as f:
                samples = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.fail(f"allSamples.txt not found at {allSamplesPath}")
        return samples

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
            if "-e" in sys.argv and "keep" in sys.argv:
                stagePath = common.sysUtils.getDefaultStagePath(".python.usda")
                print(f"\nStage output to {stagePath}")
                return_code, output = utils.shell.run_shell_script("python", "all", "-p", stagePath)
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

    def testAllSamplesConsistency(self):
        samples = self._getSamples()

        # There are some extra directories in the source directory that are not samples
        sampleDirsToIgnore = ["assetValidator", "common", "tests", "usdTraverse"]
        samples.extend(sampleDirsToIgnore)

        # Check that the samples are consistent with the directory names in the source directory
        sourceDir = pathlib.Path(__file__).parent.parent.parent / "source"
        for sampleDir in sourceDir.iterdir():
            if sampleDir.is_dir():
                sample = sampleDir.name
                if sample not in samples:
                    self.fail(f"Sample <{sample}> not found in allSamples.txt")
