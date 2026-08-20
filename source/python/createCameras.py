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

    defaultPrim = stage.GetDefaultPrim()

    # Get valid, unique child prim names for the two cameras under the default prim
    cameraNames = ["telephotoCamera", "wideCamera"]
    validTokens = usdex.core.getValidChildNames(defaultPrim, cameraNames)

    # GfCamera is a container for camera attributes, used by the Exchange SDK defineCamera function
    gfCam = Gf.Camera()

    # The Gf.Camera default clipping range assumes centimeter stages, so express the same 1 cm - 10 km range in meters
    gfCam.clippingRange = Gf.Range1f(0.01, 10000)

    # Lens and filmback values are expressed in tenths of a scene unit, so the Gf.Camera defaults (sized for a
    # centimeter stage) and the focal length must be divided by 100 for this meter stage, otherwise the physical
    # lens aperture becomes meters wide and the render is heavily defocused
    gfCam.horizontalAperture = Gf.Camera.DEFAULT_HORIZONTAL_APERTURE / 100
    gfCam.verticalAperture = Gf.Camera.DEFAULT_VERTICAL_APERTURE / 100

    # Configure the telephoto camera with a long focus distance
    gfCam.focusDistance = 88.62
    gfCam.focalLength = 1  # 100 mm
    gfCam.fStop = 1.4

    # Define the camera
    telephotoCamera = usdex.core.defineCamera(defaultPrim, validTokens[0], gfCam)

    # We could configure the xform in the GfCamera, but we can also do so with:
    usdex.core.setLocalTransform(
        xformable=telephotoCamera,
        translation=Gf.Vec3d(65.71555, -58.62940, 14.15558),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(81.474, -0.314, 47.484),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    # Configure the wide-angle camera with a shorter focus distance
    gfCam.focusDistance = 5.63
    gfCam.focalLength = 0.035  # 3.5 mm
    gfCam.fStop = 32

    # Define the camera
    wideCamera = usdex.core.defineCamera(defaultPrim, validTokens[1], gfCam)

    # We could configure the xform in the GfCamera, but we can also do so with:
    usdex.core.setLocalTransform(
        xformable=wideCamera,
        translation=Gf.Vec3d(-5.06538, -2.03795, 3.04977),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(53.976, 1.109, -45.364),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates cameras using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
