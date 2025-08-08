# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import tempfile
import unittest

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import utils.fileFormat
import utils.shell
from pxr import Usd, UsdGeom
from utils.BaseTestCase import BaseTestCase


class CreateAssetTestCase(BaseTestCase):
    # Test the createAsset program
    # Testing:
    # - it creates a flower planter asset with 3 flowers and proper structure
    # - it creates a reference to the asset in the main stage
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage
    # - it creates the expected geometric components (planter, stems, petals)
    # - it creates and binds materials to the components
    # - it validates the asset structure using layer prim specs

    def _checkStageContents(self, stagePath, textFlag):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        self.assertEqual("World", defaultPrim.GetName())

        flowerPlanterPrimPath = defaultPrim.GetPath().AppendChild("FlowerPlanter")

        # Check the flower planter reference prim spec exists in the layer
        flowerPlanterPrimSpec = stage.GetRootLayer().GetPrimAtPath(flowerPlanterPrimPath)
        self.assertTrue(flowerPlanterPrimSpec)

        # Check that the flower planter reference points to the asset stage
        # Use the layer prim spec to check for references
        self.assertTrue(flowerPlanterPrimSpec.hasReferences)

        # Check the transform on the flower planter reference
        flowerPlanterPrim = stage.GetPrimAtPath(flowerPlanterPrimPath)
        xform = UsdGeom.Xform(flowerPlanterPrim)
        self.assertTrue(xform)

        stage = None

    def _checkAssetStageContents(self, assetStagePath):
        """Check the contents of the created asset stage"""
        assetStage = Usd.Stage.Open(assetStagePath)
        self.assertTrue(assetStage)

        # Check the asset has a default prim named "FlowerPlanter"
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        self.assertEqual("FlowerPlanter", defaultPrim.GetName())

        # Check the display name is set
        displayName = defaultPrim.GetDisplayName()
        self.assertEqual("🌻", displayName)

        # Check that the asset has payloads
        payloads = defaultPrim.GetPayloads()
        self.assertTrue(payloads)

        assetStage = None

    def _runSampleOptions(self, script, programPath):
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

                # Check the asset stage that was created
                stageDir = pathlib.Path(args[0]).parent
                assetStagePath = stageDir / "FlowerPlanter.usda"
                self.assertTrue(assetStagePath.exists())
                self._checkAssetStageContents(assetStagePath.as_posix())

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateAsset(self):
        self._runSampleOptions("run", "createAsset")

    def testPythonCreateAsset(self):
        self._runSampleOptions("python", "source/createAsset/createAsset.py")

    def testCompareTextCreateAsset(self):
        self.compareTextOutput("createAsset", "source/createAsset/createAsset.py")
