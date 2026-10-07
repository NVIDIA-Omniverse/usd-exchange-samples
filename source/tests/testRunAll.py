# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import sys
import tempfile
import unittest

import common.sysUtils
import utils.shell
import utils.validation
from utils.ScopedEnvVar import ScopedEnvVar


class RunAllTestCase(unittest.TestCase):

    def _checkStage(self, stagePath):
        stagePathObj = pathlib.Path(stagePath)
        self.assertTrue(stagePathObj.exists(), f"Stage file {stagePathObj} does not exist")
        utils.validation.assertValidatorCliSucceeds(self, stagePath)

    def testRunAllCpp(self):
        if "-e" in sys.argv and "keep" in sys.argv:
            stagePath = common.sysUtils.getDefaultStagePath(".cpp.usda")
            print(f"\nStage output to {stagePath}")
            return_code, output = utils.shell.run_shell_script("run", "all", "-p", stagePath)
            self.assertEqual(return_code, 0, output)
            self._checkStage(stagePath)
        else:
            with tempfile.TemporaryDirectory() as tempDirStr:
                tempDir = pathlib.Path(tempDirStr)
                stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                return_code, output = utils.shell.run_shell_script("run", "all", "-p", stagePath)
                self.assertEqual(return_code, 0, output)
                self._checkStage(stagePath)

    def testRunAllCppMissingExecutable(self):
        with ScopedEnvVar("USDEX_SAMPLES_CONFIG", "missing-test-config", ["Windows", "Linux"]):
            return_code, output = utils.shell.run_shell_script("run", "all")
        self.assertEqual(return_code, 3, output)
        self.assertIn("missing-test-config", output)
        self.assertNotIn("=== All samples completed ===", output)

    def testRunAllPython(self):
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            pySampleBaseDir = "source/python/"
            if "-e" in sys.argv and "keep" in sys.argv:
                stagePath = common.sysUtils.getDefaultStagePath(".python.usda")
                print(f"\nStage output to {stagePath}")
                return_code, output = utils.shell.run_shell_script("python", f"{pySampleBaseDir}all.py", "-p", stagePath)
                self.assertEqual(return_code, 0, output)
                self._checkStage(stagePath)
            else:
                with tempfile.TemporaryDirectory() as tempDirStr:
                    tempDir = pathlib.Path(tempDirStr)
                    stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                    return_code, output = utils.shell.run_shell_script("python", f"{pySampleBaseDir}all.py", "-p", stagePath)
                    self.assertEqual(return_code, 0, output)
                    self._checkStage(stagePath)

    def testRunAllPythonFailure(self):
        samples = common.sysUtils.getAllSamples()
        return_code, output = utils.shell.run_shell_script("python", "source/python/all.py", "--invalid-test-argument")
        self.assertEqual(return_code, 2, output)
        self.assertIn("unrecognized arguments: --invalid-test-argument", output)
        self.assertIn(f"Error running sample {samples[0]}", output)
        self.assertNotIn(f"=== Running {samples[1]} ===", output)
        self.assertNotIn("=== All samples completed ===", output)

    def testAllSamplesConsistency(self):
        samples = common.sysUtils.getAllSamples()

        # There are some extra files and directories in the source directories that are not samples
        sampleEntriesToIgnore = ["__pycache__", "all", "validateUsd", "common", "python", "tests", "usdTraverse"]
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
