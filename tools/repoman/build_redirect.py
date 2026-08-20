# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os

from omni.repo.man.exceptions import QuietExpectedError


def setup_repo_tool(parser, config):
    parser.prog = "build"
    parser.description = "repo build has moved to build.sh/build.bat."

    def run_repo_tool(options, config):
        script = "build.bat" if os.name == "nt" else "./build.sh"

        print("repo build has moved for OpenUSD Exchange Samples.")
        print(f"Use {script} instead.")
        raise QuietExpectedError("repo build has moved")

    return run_repo_tool
