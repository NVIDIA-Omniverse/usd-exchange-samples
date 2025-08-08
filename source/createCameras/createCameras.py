# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import sys

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

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

    defaultPrim = stage.GetDefaultPrim()

    # Get valid, unique child prim names for the two cameras under the default prim
    cameraNames = ["telephotoCamera", "wideCamera"]
    validTokens = usdex.core.getValidChildNames(defaultPrim, cameraNames)

    # GfCamera is a container for camera attributes, used by the Exchange SDK defineCamera function
    gfCam = Gf.Camera()

    # Put the telephoto camera about a 3000 units from the origin and focus on the cube we created in createStage
    gfCam.focusDistance = 3000
    gfCam.focalLength = 100
    gfCam.fStop = 1.4

    # Define the camera
    telephotoCamera = usdex.core.defineCamera(defaultPrim, validTokens[0], gfCam)

    # We could configure the xform in the GfCamera, but we can also do so with:
    usdex.core.setLocalTransform(
        xformable=telephotoCamera,
        translation=Gf.Vec3d(2531.459, 49.592, 1707.792),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(-0.379, 56.203, 0.565),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    # Put the wide-angle camera about a 250 units from the origin and look towards the cube we created in createStage
    gfCam.focusDistance = 250
    gfCam.focalLength = 3.5
    gfCam.fStop = 32

    # Define the camera
    wideCamera = usdex.core.defineCamera(defaultPrim, validTokens[1], gfCam)

    # We could configure the xform in the GfCamera, but we can also do so with:
    usdex.core.setLocalTransform(
        xformable=wideCamera,
        translation=Gf.Vec3d(-283.657, 12.826, 140.9),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(-1.234, -64.0, -2.53),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates cameras using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
