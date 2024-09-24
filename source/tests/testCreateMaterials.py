# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import usdex.rtx
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom, UsdShade, UsdUtils
from utils.BaseTestCase import BaseTestCase


class CreateMaterialsTestCase(BaseTestCase):
    # Test the createMaterials program
    # Testing:
    # - it creates a mesh (UsdGeom.Mesh) under the default prim
    # - this mesh should have the correct name (depending on the children of default prim)
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage

    def _checkStageContents(self, stagePath, meshPrimName, matPrimName, sphereMatName, previewCubeName, previewMatName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the cube material
        materialScopePath = defaultPrim.GetPath().AppendPath(UsdUtils.GetMaterialsScopeName())
        prim = stage.GetPrimAtPath(materialScopePath.AppendPath(matPrimName))
        self.assertTrue(prim)
        typedPrim = UsdShade.Material(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdShade.Material)
        textureInputs = ["DiffuseTexture", "NormalTexture", "ORMTexture"]
        for textureInput in textureInputs:
            texPath = typedPrim.GetInput(textureInput).Get().path
            absPath = stage.GetRootLayer().ComputeAbsolutePath(texPath)
            self.assertTrue(pathlib.Path(absPath).exists())
        cubeMatPrim = prim

        # Check the cube
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(meshPrimName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Mesh(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Mesh)
        self.assertTrue(UsdShade.MaterialBindingAPI(prim))
        boundMatPrimPath = UsdShade.MaterialBindingAPI.ComputeBoundMaterials([prim])[0][0].GetPrim().GetPath()
        self.assertEqual(boundMatPrimPath, cubeMatPrim.GetPath())

        # Check the sphere material
        materialScopePath = defaultPrim.GetPath().AppendPath(UsdUtils.GetMaterialsScopeName())
        prim = stage.GetPrimAtPath(materialScopePath.AppendPath(sphereMatName))
        self.assertTrue(prim)
        typedPrim = UsdShade.Material(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdShade.Material)
        mdlShader = usdex.rtx.computeEffectiveMdlSurfaceShader(typedPrim)
        self.assertTrue(mdlShader.GetInput("project_uvw").Get())
        self.assertTrue(mdlShader.GetInput("world_or_object").Get())
        self.assertAlmostEqual(mdlShader.GetInput("texture_scale").Get(), Gf.Vec2f(0.01))

        # Check the Preview Surface material
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(previewCubeName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Mesh(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Mesh)
        self.assertTrue(UsdShade.MaterialBindingAPI(prim))
        boundMatPrimPath = UsdShade.MaterialBindingAPI.ComputeBoundMaterials([prim])[0][0].GetPrim().GetPath()
        previewMatPrim = stage.GetPrimAtPath(materialScopePath.AppendPath(previewMatName))
        self.assertEqual(boundMatPrimPath, previewMatPrim.GetPath())
        self.assertEqual(
            usdex.core.computeEffectivePreviewSurfaceShader(UsdShade.Material(previewMatPrim)).GetPrim().GetPath(),
            usdex.rtx.computeEffectiveMdlSurfaceShader(UsdShade.Material(previewMatPrim)).GetPrim().GetPath(),
        )

    def _runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            meshNames = ["pbrMesh", "pbrMesh_1"]
            cubeMatNames = ["cubePbr", "cubePbr_1"]
            sphereMatNames = ["sphereUvwPbr", "sphereUvwPbr_1"]
            previewCubeNames = ["previewSurfaceMesh", "previewSurfaceMesh_1"]
            previewMatNames = ["previewSurfacePbr", "previewSurfacePbr_1"]

            for args in argsRuns:
                for i in range(len(meshNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], meshNames[i], cubeMatNames[i], sphereMatNames[i], previewCubeNames[i], previewMatNames[i])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test relative path calculation in the program.  These pollute the repo, but they clean up after themselves
            localStage = "local_test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, meshNames[0], cubeMatNames[0], sphereMatNames[0], previewCubeNames[0], previewMatNames[0])
            pathlib.Path.unlink(pathlib.Path(localStage))
            shutil.rmtree("textures")

            localStage = "local_directory/test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, meshNames[0], cubeMatNames[0], sphereMatNames[0], previewCubeNames[0], previewMatNames[0])
            shutil.rmtree("local_directory")

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateMaterials(self):
        self._runSampleOptions("run", "createMaterials")

    def testPythonCreateMaterials(self):
        self._runSampleOptions("python", "source/createMaterials/createMaterials.py")

    def testCompareTextCreateMaterials(self):
        self.compareTextOutput("createMaterials", "source/createMaterials/createMaterials.py")
