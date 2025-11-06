# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import tempfile
import unittest

import usdex.core
import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom
from utils.ScopedEnvVar import ScopedEnvVar


class SetDisplayNamesTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "setDisplayNames"

    def _checkStageContents(self, stagePath, primName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the xform
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(primName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Xform(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Xform)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        self.assertNotEqual(translation, Gf.Vec3f(0))
        displayName = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(displayName, "🚀")

        self.assertEqual(len(prim.GetChildren()), 4)
        displayChars = ["⛽", "👃", "🦈", "🦈"]
        for idx, child in enumerate(prim.GetChildren()):
            self.assertTrue(displayChars[idx] in usdex.core.computeEffectiveDisplayName(child))

        stage = None

    def runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            primNames = ["rocket", "rocket_1"]

            for args in argsRuns:
                for idx in range(len(primNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])

                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], primNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
