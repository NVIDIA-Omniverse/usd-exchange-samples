# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import shutil
import tempfile
import unittest

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import usdex.core
import utils.fileFormat
import utils.shell
from pxr import Gf, Sdf, Usd, UsdGeom
from utils.BaseTestCase import BaseTestCase


class CreateReferencesTestCase(BaseTestCase):
    def _checkStageContents(self, stagePath, refPrimName, payloadPrimName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # check that the reference prim is present
        refPrim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(refPrimName))
        self.assertTrue(refPrim)
        typedPrim = UsdGeom.Xform(refPrim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Xform)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(refPrim)
        self.assertNotEqual(translation, Gf.Vec3d(0))

        # check the reference info
        refPrimSpec = stage.GetRootLayer().GetPrimAtPath(refPrim.GetPath())
        referencesInfo = refPrimSpec.GetInfo("references")
        self.assertEqual(len(referencesInfo.prependedItems), 1)

        # check that the reference stage is present
        componentStageName = pathlib.Path(referencesInfo.prependedItems[0].assetPath).name
        stageDir = pathlib.Path(stagePath).parent
        componentStagePath = stageDir / componentStageName
        self.assertTrue(componentStagePath.exists())

        # open the reference stage
        refStage = Usd.Stage.Open(componentStagePath.as_posix())
        self.assertTrue(refStage)

        # check for the layer comment
        self.assertTrue(len(refStage.GetRootLayer().comment) > 0)

        # check that the last mesh scale is different due to the override
        inComponentMesh = UsdGeom.Xformable(refStage.GetDefaultPrim().GetChildren()[-1])
        if inComponentMesh:
            inComponentTransform = usdex.core.getLocalTransform(inComponentMesh)
        inStageMesh = UsdGeom.Xformable(refPrim.GetChildren()[-1])
        if inStageMesh:
            inStageTransform = usdex.core.getLocalTransform(inStageMesh)
        self.assertNotEqual(inComponentTransform.GetScale(), inStageTransform.GetScale())
        refStage = None

        # check that the payload prim is present
        payloadPrim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(payloadPrimName))
        self.assertTrue(payloadPrim)
        typedPrim = UsdGeom.Xform(payloadPrim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Xform)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(payloadPrim)
        self.assertNotEqual(translation, Gf.Vec3d(0))

        # check the payload info
        payloadPrimSpec = stage.GetRootLayer().GetPrimAtPath(payloadPrim.GetPath())
        payloadsInfo = payloadPrimSpec.GetInfo("payload")
        self.assertEqual(len(payloadsInfo.prependedItems), 1)

        # check that the reference stage is present
        componentStageName = pathlib.Path(payloadsInfo.prependedItems[0].assetPath).name
        stageDir = pathlib.Path(stagePath).parent
        componentStagePath = stageDir / componentStageName
        self.assertTrue(componentStagePath.exists())

        # open the payload stage
        payloadStage = Usd.Stage.Open(componentStagePath.as_posix())
        self.assertTrue(payloadStage)

        # check for the layer comment
        self.assertTrue(len(payloadStage.GetRootLayer().comment) > 0)

        # check that the last mesh display color is different due to the override
        inComponentMesh = UsdGeom.Mesh(payloadStage.GetDefaultPrim().GetChildren()[-1])
        if inComponentMesh:
            inComponentTransform = usdex.core.getLocalTransform(inComponentMesh)
            primvar = inComponentMesh.GetDisplayColorPrimvar()
            inComponentColorData = usdex.core.Vec3fPrimvarData.getPrimvarData(primvar)
            self.assertEqual(inComponentColorData.interpolation(), UsdGeom.Tokens.constant)
        inStageMesh = UsdGeom.Mesh(payloadPrim.GetChildren()[-1])
        if inStageMesh:
            primvar = inStageMesh.GetDisplayColorPrimvar()
            inStageColorData = usdex.core.Vec3fPrimvarData.getPrimvarData(primvar)
            self.assertEqual(inStageColorData.interpolation(), UsdGeom.Tokens.constant)
        self.assertNotEqual(inStageColorData.values(), inComponentColorData.values())
        payloadStage = None
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
            refNames = ["referencePrim", "referencePrim_1"]
            payloadNames = ["payloadPrim", "payloadPrim_1"]

            for args in argsRuns:
                for idx in range(len(refNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])

                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], refNames[idx], payloadNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test relative path calculation in the program.  These pollute the repo, but they clean up after themselves
            localStage = "local_test_stage.usdc"
            cubeStage = "Cube_2x2x2.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, refNames[0], payloadNames[0])
            pathlib.Path.unlink(pathlib.Path(localStage))
            pathlib.Path.unlink(pathlib.Path(cubeStage))

            localStage = "local_directory/test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, refNames[0], payloadNames[0])
            shutil.rmtree("local_directory")

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateReferences(self):
        self._runSampleOptions("run", "createReferences")

    def testPythonCreateReferences(self):
        self._runSampleOptions("python", "source/createReferences/createReferences.py")

    def testCompareTextCreateReferences(self):
        # This should also verify that the reference stage file is the same
        self.compareTextOutput("createReferences", "source/createReferences/createReferences.py")
