# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import pathlib
import platform
import subprocess
import sys

import common.sysUtils


def main():
    samples = common.sysUtils.getAllSamples()
    for sample in samples:
        print(f"=== Running {sample} === ")
        cmdline = [sys.executable]
        samplePath = pathlib.Path(__file__).parent / f"{sample}.py"
        cmdline.append(samplePath.as_posix())
        if len(sys.argv) > 1:
            cmdline.extend(sys.argv[1:])

        env = os.environ.copy()
        if platform.system() == "Windows":
            # On Windows, ensure UTF-8 output for Python scripts
            env["PYTHONIOENCODING"] = "utf-8"
        completed = subprocess.run(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", env=env)
        if completed.returncode != 0:
            print(f"Error running sample {sample}: {completed.stdout}")
        else:
            print(completed.stdout)
    print("=== All samples completed ===")


if __name__ == "__main__":
    main()
