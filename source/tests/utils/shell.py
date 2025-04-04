# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import os
import platform
import subprocess


def shell_ext():
    if platform.system() == "Windows":
        return ".bat"
    else:
        return ".sh"


def run_shell_script(script, *argv):
    cmdline = list()
    cmdline.append(os.path.join(os.getcwd(), script + shell_ext()))
    cmdline += argv
    # clean the environment to ensure local system LD_LIBRARY_PATH
    # does not interfere with subprocess tests
    env = os.environ.copy()
    if platform.system() == "Linux" and "LD_LIBRARY_PATH" in env:
        del env["LD_LIBRARY_PATH"]
    completed = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", env=env)
    return completed.returncode, completed.stdout
