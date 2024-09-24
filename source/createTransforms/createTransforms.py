# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


def findXformable(stage) -> UsdGeom.Xformable:
    """
    Find a UsdGeom.Xformable prim using a simple stage traversal.

    Args:
        stage: A valid stage to traverse

    Returns: A UsdGeom.Xformable (only valid if found)
    """
    for node in stage.Traverse():
        if node.IsA(UsdGeom.Xformable):
            return UsdGeom.Xformable(node)

    # Could not a valid Xformable prim
    return UsdGeom.Xformable()


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    # Find or create a xformable prim and rotate it using individual components
    xformable = findXformable(stage)
    if not xformable:
        xformable = UsdGeom.Xformable(common.usdUtils.createCube(stage.GetDefaultPrim(), "cube"))

    print(f"Rotating xformable <{xformable.GetPrim().GetPath()}> 45 degrees in the Y axis")
    translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(xformable.GetPrim())
    rotation += Gf.Vec3f(0, 45, 0)
    usdex.core.setLocalTransform(
        prim=xformable.GetPrim(),
        translation=translation,
        pivot=pivot,
        rotation=rotation,
        rotationOrder=rotationOrder,
        scale=scale,
    )

    # Create a Xform prim with an initial transform
    primNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["groundXform"])
    transform = Gf.Transform(Gf.Vec3d(0, -55, 0))
    xformPrim = usdex.core.defineXform(parent=stage.GetDefaultPrim(), name=primNames[0], transform=transform)

    # Create a "ground plane" cube that is scaled, use the GfMatrix arg to set the transform
    transform = Gf.Transform()
    transform.SetScale(Gf.Vec3d(20, 0.1, 20))
    cube = common.usdUtils.createCube(xformPrim.GetPrim(), "groundCube")
    usdex.core.setLocalTransform(prim=cube.GetPrim(), matrix=transform.GetMatrix())

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create transforms using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
