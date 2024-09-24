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
from pxr import Usd, UsdGeom
from utils.BaseTestCase import BaseTestCase


class CreateCamerasTestCase(BaseTestCase):
    def _checkStageContents(self, stagePath, telephotoCameraName, wideCameraName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the telephoto camera existence, translation, and other properties
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(telephotoCameraName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Camera(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Camera)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        focusDistance = typedPrim.GetFocusDistanceAttr().Get()
        self.assertAlmostEqual(translation.GetLength() / focusDistance, 1, 0)
        self.assertAlmostEqual(typedPrim.GetFStopAttr().Get(), 1.4)

        # Check the wide camera existence, translation, and other properties
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(wideCameraName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Camera(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Camera)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        focusDistance = typedPrim.GetFocusDistanceAttr().Get()
        self.assertAlmostEqual(translation.GetLength() / focusDistance, 1, 0)
        self.assertAlmostEqual(typedPrim.GetFStopAttr().Get(), 32)

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
            telephotoCameraNames = ["telephotoCamera", "telephotoCamera_1"]
            wideCameraNames = ["wideCamera", "wideCamera_1"]

            for args in argsRuns:
                for idx in range(len(telephotoCameraNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])

                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], telephotoCameraNames[idx], wideCameraNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateCameras(self):
        self._runSampleOptions("run", "createCameras")

    def testPythonCreateCameras(self):
        self._runSampleOptions("python", "source/createCameras/createCameras.py")

    def testCompareTextCreateCameras(self):
        self.compareTextOutput("createCameras", "source/createCameras/createCameras.py")
