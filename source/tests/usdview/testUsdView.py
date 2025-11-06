# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import pathlib
import platform
import subprocess
import unittest


def shell_ext():
    if platform.system() == "Windows":
        return ".bat"
    else:
        return ".sh"


class UsdViewTestCase(unittest.TestCase):
    def testUsdView(self):
        stagePath = pathlib.Path(__file__).parent.parent.parent / "usdTraverse" / "sample.usda"
        stagePath = stagePath.as_posix()
        env = os.environ.copy()
        if platform.system() == "Linux" and "LD_LIBRARY_PATH" in env:
            del env["LD_LIBRARY_PATH"]

        scriptPath = pathlib.Path(__file__).parent.parent.parent.parent / f"usdview{shell_ext()}"
        print(f"scriptPath: {scriptPath}")
        cmdline = [scriptPath, "--quitAfterStartup", "--norender", stagePath]
        completed = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", env=env)
        self.assertEqual(completed.returncode, 0, completed.stdout)
