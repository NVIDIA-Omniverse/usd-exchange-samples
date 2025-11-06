# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import platform
import subprocess
import sys


def shell_ext():
    if platform.system() == "Windows":
        return ".bat"
    else:
        return ".sh"


def run_shell_script(script, *argv):
    cmdline = list()
    if "python" in script:
        # Use sys.executable to ensure we use the same Python interpreter (respects venv)
        cmdline.append(sys.executable)
    else:
        cmdline.append(os.path.join(os.getcwd(), script + shell_ext()))
    cmdline += argv

    env = os.environ.copy()
    completed = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", env=env)
    return completed.returncode, completed.stdout
