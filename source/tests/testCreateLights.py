# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import shutil
import tempfile
import unittest

import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom, UsdLux


class CreateLightsTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createLights"

    # Test the createLights program
    # Testing:
    # - it creates a rect and dome light (UsdLux.RectLight, UsdLux.DomeLight) under the default prim
    # - these lights should have the correct name (depending on the children of default prim)
    # - it checks that the texture file attribute is present on the dome light
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage

    def _checkStageContents(self, stagePath, rectLightPrimName, domeLightPrimName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the rectLight
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(rectLightPrimName))
        self.assertTrue(prim)
        typedPrim = UsdLux.RectLight(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdLux.RectLight)
        lightApi = UsdLux.LightAPI(prim)
        translation = UsdGeom.Xformable(prim).GetLocalTransformation().ExtractTranslation()
        self.assertTrue(Gf.IsClose(translation, Gf.Vec3d(0.0, 0.0, 0.6), 0.00001))
        self.assertEqual(typedPrim.GetWidthAttr().Get(), 0.25)
        self.assertEqual(typedPrim.GetHeightAttr().Get(), 0.25)
        self.assertEqual(lightApi.GetIntensityAttr().Get(), 500.0)
        self.assertEqual(lightApi.GetColorAttr().Get(), Gf.Vec3f(0.3, 0.0, 1.0))

        # Check the domeLight
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(domeLightPrimName))
        self.assertTrue(prim)
        typedPrim = UsdLux.DomeLight(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdLux.DomeLight)

        # Check that the dome orientation follows the stage up-axis
        xformOps = UsdGeom.Xformable(typedPrim).GetOrderedXformOps()
        self.assertEqual(len(xformOps), 1)
        self.assertEqual(xformOps[0].GetOpName(), "xformOp:rotateX:orientToStageUpAxis")
        self.assertEqual(xformOps[0].Get(), 90.0)

        # Check that the guide radius represents the previous 1 km guide size in meter units
        self.assertEqual(typedPrim.GetGuideRadiusAttr().Get(), 1000.0)

        # Check the existance of the domelight texture
        textureFilePath = typedPrim.GetTextureFileAttr().Get()
        textureFilePathFromStage = pathlib.Path(stagePath).parent / pathlib.Path(textureFilePath.path)
        self.assertTrue(len(textureFilePath.path) > 0)
        self.assertTrue(textureFilePathFromStage.exists())

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
            rectLightNames = ["rectLight", "rectLight_1"]
            domeLightNames = ["domeLight", "domeLight_1"]

            for args in argsRuns:
                for idx in range(len(rectLightNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])

                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], rectLightNames[idx], domeLightNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test relative path calculation in the program.  These pollute the repo, but they clean up after themselves
            localStage = "local_test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, rectLightNames[0], domeLightNames[0])
            pathlib.Path.unlink(pathlib.Path(localStage))
            shutil.rmtree("textures")

            localStage = "local_directory/test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, rectLightNames[0], domeLightNames[0])
            shutil.rmtree("local_directory")

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
