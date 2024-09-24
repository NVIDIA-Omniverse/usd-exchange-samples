# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
    completed = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    return completed.returncode, completed.stdout
