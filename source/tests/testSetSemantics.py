# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import shutil
import tempfile

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import utils.fileFormat
import utils.shell
from pxr import Usd, UsdSemantics
from utils.BaseTestCase import BaseTestCase
from utils.ScopedEnvVar import ScopedEnvVar


class SetSemanticsTestCase(BaseTestCase):
    def _checkStageContents(self, stagePath, textFlag):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)
        self.assertEqual("World", defaultPrim.GetName())

        # Check the semantics
        # Q3947 for house:  https://www.wikidata.org/wiki/Q3947
        # Q42948 for wall:  https://www.wikidata.org/wiki/Q42948
        # Q83180 for roof:  https://www.wikidata.org/wiki/Q83180
        # Q36794 for door:  https://www.wikidata.org/wiki/Q36794
        # Q35473 for window:  https://www.wikidata.org/wiki/Q35473
        semantics_data = [
            ("/World/house", ["Q3947"]),
            ("/World/house/wall", ["Q3947", "Q42948"]),
            ("/World/house/roof", ["Q3947", "Q83180"]),
            ("/World/house/door", ["Q36794", "Q3947"]),
            ("/World/house/window", ["Q35473", "Q3947"]),
        ]
        for data in semantics_data:
            prim = stage.GetPrimAtPath(data[0])
            self.assertTrue(prim)
            self.assertTrue(prim.HasAPI(UsdSemantics.LabelsAPI))
            query = UsdSemantics.LabelsQuery("wikidata_qcode", Usd.TimeCode.Default())
            self.assertEqual(query.ComputeUniqueInheritedLabels(prim), data[1])

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

            for args in argsRuns:
                if args[1]:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                else:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(args[0], args[1])
                utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppSetSemantics(self):
        self._runSampleOptions("run", "setSemantics")

    def testPythonSetSemantics(self):
        self._runSampleOptions("python", "source/setSemantics/setSemantics.py")

    def testCompareTextSetSemantics(self):
        self.compareTextOutput("setSemantics", "source/setSemantics/setSemantics.py")
