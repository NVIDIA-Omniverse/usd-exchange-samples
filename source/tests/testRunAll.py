# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
    def _loopSamples(self, script, stagePath):
        samples = [
            "createStage",
            "createCameras",
            "createLights",
            "createMaterials",
            "createMesh",
            "createReferences",
            "createSkeleton",
            "createTransforms",
            "setDisplayNames",
        ]

        for sample in samples:
            if "run" in script:
                program = sample
            else:
                sampleScript = sample + ".py"
                source = pathlib.Path("source")
                program = pathlib.Path(source / sample / sampleScript).as_posix()
            return_code, output = utils.shell.run_shell_script(script, program, "-p", stagePath)
            self.assertEqual(return_code, 0, output)

    def testRunAllCpp(self):
        if "-e" in sys.argv and "keep" in sys.argv:
            stagePath = common.sysUtils.getDefaultStagePath(".cpp.usda")
            print(f"\nStage output to {stagePath}")
            self._loopSamples("run", stagePath)
        else:
            with tempfile.TemporaryDirectory() as tempDirStr:
                tempDir = pathlib.Path(tempDirStr)
                stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                self._loopSamples("run", stagePath)

    def testRunAllPython(self):
        with ScopedEnvVar("PYTHONIOENCODING", "utf-8", ["Windows"]):
            if "-e" in sys.argv and "keep" in sys.argv:
                stagePath = common.sysUtils.getDefaultStagePath(".python.usda")
                print(f"\nStage output to {stagePath}")
                self._loopSamples("python", stagePath)
            else:
                with tempfile.TemporaryDirectory() as tempDirStr:
                    tempDir = pathlib.Path(tempDirStr)
                    stagePath = pathlib.Path(tempDir / "test_stage.usdc").as_posix()
                    self._loopSamples("python", stagePath)
