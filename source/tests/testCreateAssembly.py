# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import tempfile
import unittest

import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Kind, Usd, UsdGeom


class CreateAssemblyTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createAssembly"

    def _checkStageContents(self, stagePath, textFlag):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        self.assertEqual("World", defaultPrim.GetName())

        # Check that the default prim is an assembly
        self.assertTrue(Usd.ModelAPI(defaultPrim).GetKind() == Kind.Tokens.group)
        # Check that the pinewood derby prim is an assembly
        derbyPrim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild("PinewoodDerbyAssembly"))
        self.assertTrue(Usd.ModelAPI(derbyPrim).GetKind() == Kind.Tokens.assembly)
        # Check that the child prims are components
        for childPrim in derbyPrim.GetChildren():
            self.assertTrue(Usd.ModelAPI(childPrim).GetKind() == Kind.Tokens.component, msg=f"Child prim {childPrim.GetName()} is not a component")

        # Check for a blue and green car
        CAR_BODY_COLOR_PRIMVAR = "bodyPaintColor"
        blueCarPrim = derbyPrim.GetPrimAtPath(derbyPrim.GetPath().AppendChild("BlueCar"))
        self.assertTrue(blueCarPrim)
        blueCarColor = UsdGeom.PrimvarsAPI(blueCarPrim.GetPrim()).GetPrimvar(CAR_BODY_COLOR_PRIMVAR).Get()
        self.assertEqual(blueCarColor[0], Gf.Vec3f(0.3284, 0.7490, 0.7098))

        greenCarPrim = derbyPrim.GetPrimAtPath(derbyPrim.GetPath().AppendChild("GreenCar"))
        self.assertTrue(greenCarPrim)
        greenCarColor = UsdGeom.PrimvarsAPI(greenCarPrim.GetPrim()).GetPrimvar(CAR_BODY_COLOR_PRIMVAR).Get()
        self.assertEqual(greenCarColor[0], Gf.Vec3f(0.294, 0.725, 0))

    def _checkAssetStageContents(self, assetStagePath):
        """Check the contents of the created asset stage"""
        assetStage = Usd.Stage.Open(assetStagePath)
        self.assertTrue(assetStage)

        # Check the assembly has a default prim named correctly - the same name as the stage identifier
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        assetStageName = pathlib.Path(assetStagePath).stem
        self.assertEqual(assetStageName, defaultPrim.GetName())

        # Check that the asset has payloads
        payloads = defaultPrim.GetPayloads()
        self.assertTrue(payloads)

    def runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]

            for args in argsRuns:
                if args[1]:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                else:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(args[0], args[1])
                utils.fileFormat.checkLayerFormat(self, args[0], args[1])

                # Check the asset stages
                assetStageNames = ["PinewoodDerbyTrack", "PinewoodDerbyCar"]
                for assetStageName in assetStageNames:
                    stageDir = pathlib.Path(args[0]).parent
                    assetStagePath = stageDir / assetStageName / f"{assetStageName}.usda"
                    self.assertTrue(assetStagePath.exists())
                    self._checkAssetStageContents(assetStagePath.as_posix())
            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
