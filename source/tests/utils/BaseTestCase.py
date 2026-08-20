# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import difflib
import filecmp
import pathlib
import tempfile
from abc import abstractmethod

import usdex.test
import utils.fileFormat
import utils.shell
from pxr import Ar
from utils.ScopedEnvVar import ScopedEnvVar

from source.validateUsd.validateUsdBootstrap import getCoreMaterialsPath


class BaseTestCase(usdex.test.TestCase):

    @property
    @abstractmethod
    def sampleName(self):
        """The name of the sample to test"""
        raise NotImplementedError()

    @abstractmethod
    def runSampleOptions(self, script, programPath):
        """The function to run the sample options"""
        raise NotImplementedError()

    def runAssetValidator(self, stagePath):
        resolverContext = Ar.DefaultResolverContext([getCoreMaterialsPath()])
        with Ar.ResolverContextBinder(resolverContext):
            self.assertIsValidUsd(stagePath)

    def compareTextOutput(self, cppName, pythonScript):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            stagePaths = [pathlib.Path(tempDir / "cpp" / "test.usda").as_posix(), pathlib.Path(tempDir / "python" / "test.usda").as_posix()]
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

            # Enumerate the files in the cpp and python directories
            cppFiles = sorted(pathlib.Path(tempDir / "cpp").rglob("*.*"))
            pythonFiles = sorted(pathlib.Path(tempDir / "python").rglob("*.*"))

            cppFileNames = [f.name for f in cppFiles]
            pythonFileNames = [f.name for f in pythonFiles]
            self.assertListEqual(cppFileNames, pythonFileNames)

            ignoreSuffixes = [".png", ".exr"]
            for cppFile, pythonFile in zip(cppFiles, pythonFiles):
                if cppFile.suffix not in ignoreSuffixes:
                    filecmp.clear_cache()
                    self.assertTrue(
                        filecmp.cmp(cppFile.as_posix(), pythonFile.as_posix()), msg=printUsdFiles([cppFile.as_posix(), pythonFile.as_posix()])
                    )

    def checkUsdzOutput(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            stagePath = pathlib.Path(tempDir / "test_stage.usdc")
            usdzPath = stagePath.with_suffix(".usdz")
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", stagePath.as_posix(), "--usdz")
            self.assertEqual(return_code, 0, output)
            self.assertNotIn("Error creating USDZ package", output)
            self.assertNotIn("Failed to resolve reference", output)
            self.assertTrue(stagePath.exists(), f"Stage {stagePath} does not exist")
            utils.fileFormat.checkUsdzPackage(self, usdzPath.as_posix(), [stagePath.name])

    def testCpp(self):
        self.runSampleOptions("run", self.sampleName)

    def testCppUsdz(self):
        self.checkUsdzOutput("run", self.sampleName)

    def testPython(self):
        # Set PYTHONIOENCODING because subprocess.run() isn't giving a good default code page for the rocket glyph to print
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            self.runSampleOptions("python", f"source/python/{self.sampleName}.py")

    def testPythonUsdz(self):
        # Set PYTHONIOENCODING because subprocess.run() isn't giving a good default code page for the rocket glyph to print
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            self.checkUsdzOutput("python", f"source/python/{self.sampleName}.py")

    def testCompareText(self):
        # Set PYTHONIOENCODING because subprocess.run() isn't giving a good default code page for the rocket glyph to print
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            self.compareTextOutput(self.sampleName, f"source/python/{self.sampleName}.py")
