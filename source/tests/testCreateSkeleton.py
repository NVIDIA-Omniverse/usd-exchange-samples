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
from pxr import Gf, Usd, UsdGeom, UsdSkel
from utils.BaseTestCase import BaseTestCase


class CreateSkeletonTestCase(BaseTestCase):
    def _checkStageContents(self, stagePath, skelRootName):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        # Check the skelRoot
        prim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(skelRootName))
        self.assertTrue(prim)
        typedPrim = UsdSkel.Root(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdSkel.Root)
        translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(prim)
        self.assertNotEqual(translation, Gf.Vec3f(0))

        # Check the animation
        animPrimPath = defaultPrim.GetPath().AppendChild(skelRootName).AppendChild("anim")
        prim = stage.GetPrimAtPath(animPrimPath)
        self.assertTrue(prim)
        typedPrim = UsdSkel.Animation(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdSkel.Animation)
        transforms = typedPrim.GetTransforms(Usd.TimeCode(0))
        self.assertEqual(len(transforms), 2)
        transforms = typedPrim.GetTransforms(Usd.TimeCode(47))
        self.assertEqual(len(transforms), 2)

        # Check the skeleton
        skelPrimPath = defaultPrim.GetPath().AppendChild(skelRootName).AppendChild("skel")
        prim = stage.GetPrimAtPath(skelPrimPath)
        self.assertTrue(prim)
        typedPrim = UsdSkel.Skeleton(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdSkel.Skeleton)
        self.assertEqual(len(typedPrim.GetJointsAttr().Get()), 3)
        bindingApi = UsdSkel.BindingAPI(prim)
        self.assertTrue(bindingApi)
        self.assertEqual(bindingApi.GetAnimationSourceRel().GetTargets()[0], animPrimPath)

        # Check the mesh
        meshPrimPath = defaultPrim.GetPath().AppendChild(skelRootName).AppendChild("skinnedMesh")
        prim = stage.GetPrimAtPath(meshPrimPath)
        self.assertTrue(prim)
        typedPrim = UsdGeom.Mesh(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Mesh)
        self.assertEqual(len(typedPrim.GetPointsAttr().Get()), 6)
        bindingApi = UsdSkel.BindingAPI(prim)
        self.assertTrue(bindingApi)
        self.assertEqual(bindingApi.GetSkeletonRel().GetTargets()[0], skelPrimPath)
        self.assertEqual(len(bindingApi.GetJointWeightsPrimvar().Get()), 6)

    def _runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            skelRootNames = ["skelRootGroup", "skelRootGroup_1"]

            for args in argsRuns:
                for idx in range(len(skelRootNames)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], skelRootNames[idx])
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateSkeleton(self):
        self._runSampleOptions("run", "createSkeleton")

    def testPythonCreateSkeleton(self):
        self._runSampleOptions("python", "source/createSkeleton/createSkeleton.py")

    def testCompareTextCreateSkeleton(self):
        self.compareTextOutput("createSkeleton", "source/createSkeleton/createSkeleton.py")
