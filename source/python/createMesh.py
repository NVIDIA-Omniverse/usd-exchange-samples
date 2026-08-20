# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Usd, UsdGeom


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    meshPrim = common.usdUtils.createCubeMesh(stage.GetDefaultPrim(), "cubeMesh", 0.5, Gf.Vec3d(0.0, 0.0, 1.5))
    if not meshPrim:
        print("Failure to create mesh prim")
        sys.exit(-1)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a mesh using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
