# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import shutil
import tempfile
import unittest

import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Usd, UsdLux


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

        # Check the domeLight
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(domeLightPrimName))
        self.assertTrue(prim)
        typedPrim = UsdLux.DomeLight(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdLux.DomeLight)

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
