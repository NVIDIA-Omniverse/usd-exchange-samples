# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys

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

    print(f"Rotating xformable <{xformable.GetPrim().GetPath()}> 45 degrees in the Z axis")
    translation, pivot, rotation, rotationOrder, scale = usdex.core.getLocalTransformComponents(xformable)
    rotation += Gf.Vec3f(0, 0, 45)
    usdex.core.setLocalTransform(
        xformable=xformable,
        translation=translation,
        pivot=pivot,
        rotation=rotation,
        rotationOrder=rotationOrder,
        scale=scale,
    )

    # Create a Xform prim with an initial transform matrix
    validToken = usdex.core.getValidChildName(stage.GetDefaultPrim(), "matrixXform")
    # Matrix with scale 0.5, translation (1, -1, 0.22), rotation approx. (13.49, -20.70, 24.15) XYZ
    # Note: GfMatrix4d constructor is row-major. For USD, translation belongs in the last row.
    # fmt: off
    matrix = Gf.Matrix4d(0.42677669529663687,   0.19134171618254486, 0.17677669529663687, 0.0,
                         -0.23654367531291015,  0.42677669529663687, 0.10912718277836225, 0.0,
                         -0.10912718277836225, -0.17677669529663687, 0.45479804086963466, 0.0,
                         1.0,                  -1.0,                 0.22,                1.0,)
    # fmt: on
    matrixXformPrim = usdex.core.defineXform(stage.GetDefaultPrim(), validToken, matrix)
    common.usdUtils.createCube(matrixXformPrim.GetPrim(), name="matrixCube", displayColor=Gf.Vec3f(0.5, 0.7, 1.0))

    # Create a Xform prim with an initial transform
    primNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["groundXform"])
    transform = Gf.Transform(Gf.Vec3d(0, 0, -0.55))
    xformPrim = usdex.core.defineXform(parent=stage.GetDefaultPrim(), name=primNames[0], transform=transform)

    # Create a "ground plane" cube that is scaled, use the GfMatrix arg to set the transform
    transform = Gf.Transform()
    transform.SetScale(Gf.Vec3d(20, 20, 0.1))
    cube = common.usdUtils.createCube(xformPrim.GetPrim(), "groundCube")
    usdex.core.setLocalTransform(xformable=cube, matrix=transform.GetMatrix())

    # Create a cube with translation-orientation-scale xformOps
    quatCube = common.usdUtils.createCube(stage.GetDefaultPrim(), "quatCube")
    # Calculate the height of the cube over the ground plane
    #     /\
    #    /  \
    #   /    \ ___
    #   \    /  |
    #    \  /   | centerHeight
    #   __\/____|_
    edgeLength = quatCube.GetSizeAttr().Get()
    centerHeight = pow((edgeLength * edgeLength) / 2, 0.5)
    cubeHeight = centerHeight - 0.5  # Adjust for the height and thickness of the ground plane

    # Set the orientation as a quaternion with a 45 degree rotation around the X axis - Gf.Quatf(real, i, j, k)
    quat = Gf.Quatf(0.9238795, 0.38268343, 0, 0)
    usdex.core.setLocalTransform(xformable=quatCube, translation=Gf.Vec3d(3, 3, cubeHeight), orientation=quat)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create transforms using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
