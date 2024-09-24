# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import tempfile

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import utils.shell
from pxr import Usd
from utils.BaseTestCase import BaseTestCase


class AssetValidatorTestCase(BaseTestCase):
    def testProblemsFoundAndNoFix(self):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            stagePath = pathlib.Path(tempDir / "test_stage.usda").as_posix()
            return_code, output = utils.shell.run_shell_script("run", "createMesh", "-p", stagePath)
            self.assertEqual(return_code, 0, output)

            # This should not assert
            self.runAssetValidator(stagePath)

            # Make the stage less valid
            stage = Usd.Stage.Open(stagePath)
            meshPrim = stage.GetPrimAtPath("/World/cubeMesh")
            self.assertTrue(meshPrim)
            meshPrim.GetAttribute("extent").Clear()
            stage.Save()

            # Run this twice to make sure that "--no-fix" is default behavior
            for i in range(2):
                return_code, output = utils.shell.run_shell_script("omni_asset_validator", stagePath)
                self.assertEqual(return_code, 0, output)
                foundError = False
                for line in output.splitlines():
                    if line.lower().startswith("error"):
                        foundError = True
                self.assertTrue(foundError)
