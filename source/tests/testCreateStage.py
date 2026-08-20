# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import shutil
import tempfile
import unittest

import common.sysUtils
import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom, UsdLux
from utils.ScopedEnvVar import ScopedEnvVar


class CreateStageTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createStage"

    def _checkStageContents(self, stagePath, textFlag):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        self.assertEqual("World", defaultPrim.GetName())

        # Check the cube
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild("cube"))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Cube(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Cube)

        # Check the light
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild("distantLight"))
        self.assertTrue(prim)
        typedPrim = UsdLux.DistantLight(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdLux.DistantLight)
        self.assertEqual(typedPrim.GetIntensityAttr().Get(), 1000.0)
        self.assertEqual(prim.GetAttribute("xformOp:rotateXYZ").Get(), Gf.Vec3f(20.0, 0.0, 10.0))
        self.assertIn("xformOp:rotateXYZ", [str(token) for token in prim.GetAttribute("xformOpOrder").Get()])

        stage = None

    def runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usd").as_posix(), "--usda"),
            ]

            for args in argsRuns:
                if args[1]:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                else:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(args[0], args[1])
                utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test default options
            # Override the TMPDIR env var on Linux to steer the USD C++ pxr::ArchGetTmpDir()
            # to using the same temp dir as Python, only for this test
            #  Linux C++ temp directory (from USD fileSystem): /var/tmp
            #  Linux Python temp directory: /tmp
            with ScopedEnvVar("TMPDIR", tempfile.gettempdir(), ["Linux"]):
                defaultStagePath = common.sysUtils.getDefaultStagePath(".usdc")
                defaultStageDir = pathlib.Path(defaultStagePath).parent
                return_code, output = utils.shell.run_shell_script(script, programPath)
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(defaultStagePath, None)
                shutil.rmtree(defaultStageDir)

                defaultStagePath = common.sysUtils.getDefaultStagePath(".usda")
                return_code, output = utils.shell.run_shell_script(script, programPath, "--usda")
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(defaultStagePath, "--usda")
                shutil.rmtree(defaultStageDir)

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
