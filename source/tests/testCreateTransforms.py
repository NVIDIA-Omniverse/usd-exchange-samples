# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import tempfile
import unittest

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import usdex.core
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom
from utils.BaseTestCase import BaseTestCase


class CreateTransformsTestCase(BaseTestCase):
    def _checkStageContents(self, stagePath, cubeName, xformName, groundName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the cube
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(cubeName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Cube(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Cube)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        self.assertNotEqual(rotation, Gf.Vec3f(0))

        # Check the xform
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(xformName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Xform(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Xform)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        self.assertAlmostEqual(translation, Gf.Vec3f(0, -55, 0))

        # check the ground cube under the xform prim
        prim = stage.GetPrimAtPath(prim.GetPath().AppendChild(groundName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Cube(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Cube)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        self.assertAlmostEqual(scale, Gf.Vec3f(20, 0.1, 20))

        stage = None

    def _runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            cubeNames = ["cube", "cube"]
            xformNames = ["groundXform", "groundXform_1"]
            groundNames = ["groundCube", "groundCube"]

            for args in argsRuns:
                for idx in range(len(cubeNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])

                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], cubeNames[idx], xformNames[idx], groundNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateTransforms(self):
        self._runSampleOptions("run", "createTransforms")

    def testPythonCreateTransforms(self):
        self._runSampleOptions("python", "source/createTransforms/createTransforms.py")

    def testCompareTextCreateTransforms(self):
        self.compareTextOutput("createTransforms", "source/createTransforms/createTransforms.py")
