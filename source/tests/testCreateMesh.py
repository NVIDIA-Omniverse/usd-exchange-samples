# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import tempfile
import unittest

import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Usd, UsdGeom


class CreateMeshTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createMesh"

    # Test the createMesh program
    # Testing:
    # - it creates a mesh (UsdGeom.Mesh) under the default prim
    # - this mesh should have the correct name (depending on the children of default prim)
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage

    def _checkStageContents(self, stagePath, meshPrimName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the cube
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(meshPrimName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Mesh(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Mesh)

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
            meshNames = ["cubeMesh", "cubeMesh_1"]

            for args in argsRuns:
                for meshName in meshNames:
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], meshName)
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # A .usdz path is not a writable stage path; USDZ packaging is only enabled by --usdz
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdz").as_posix())
            self.assertNotEqual(return_code, 0, output)

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
