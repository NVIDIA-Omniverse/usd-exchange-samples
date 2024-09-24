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
from pxr import Gf, Usd


# Construct a rocket of a Cylinder, Cone, and Cubes as children of an Xform prim
# Set their display names at the end to include 🚀
def createRocket(stage):
    transform = Gf.Transform()

    # Create Xform prim with an initial transform
    validTokens = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["rocket"])
    transform.SetTranslation(Gf.Vec3d(0, 0, -300))
    xformPrim = usdex.core.defineXform(stage.GetDefaultPrim(), validTokens[0], transform)

    #################################
    # Create cylindrical rocket tube
    #################################
    cylinder = common.usdUtils.createCylinder(xformPrim.GetPrim(), "tube")
    # Set the translation
    transform.SetTranslation(Gf.Vec3d(0, 150, 0))
    usdex.core.setLocalTransform(cylinder.GetPrim(), transform)

    #################################
    # Create nose cone
    #################################
    cone = common.usdUtils.createCone(xformPrim.GetPrim(), "nose")
    # Set the translation
    transform.SetIdentity()
    transform.SetTranslation(Gf.Vec3d(0, 400, 0))
    usdex.core.setLocalTransform(cone.GetPrim(), transform)

    #################################
    # Create cube fin 1
    #################################
    fin1 = common.usdUtils.createCube(xformPrim.GetPrim(), "fin")
    # Set the scale
    transform.SetIdentity()
    transform.SetScale(Gf.Vec3d(0.01, 1, 2))
    usdex.core.setLocalTransform(fin1.GetPrim(), transform)

    #################################
    # Create cube fin 2
    #################################
    fin2 = common.usdUtils.createCube(xformPrim.GetPrim(), "fin")
    # Set the scale
    transform.SetIdentity()
    transform.SetScale(Gf.Vec3d(2, 1, 0.01))
    usdex.core.setLocalTransform(fin2.GetPrim(), transform)

    #################################
    # Access prim display names
    #################################
    origDisplayName = usdex.core.getDisplayName(xformPrim.GetPrim())
    origEffectiveName = usdex.core.computeEffectiveDisplayName(xformPrim.GetPrim())

    #################################
    # Apply prim display names
    #################################
    usdex.core.setDisplayName(xformPrim.GetPrim(), "🚀")
    usdex.core.setDisplayName(cylinder.GetPrim(), "⛽ tube")
    usdex.core.setDisplayName(cone.GetPrim(), "👃 nose")
    usdex.core.setDisplayName(fin1.GetPrim(), "🦈 fin")
    usdex.core.setDisplayName(fin2.GetPrim(), "🦈 fin")

    ###############################################
    # Access and report updated prim display names
    ###############################################
    curEffectiveName = usdex.core.computeEffectiveDisplayName(xformPrim.GetPrim())
    print(f"Xform prim display name status:")
    print(f" original getDisplayName():              <{origDisplayName}>")
    print(f" original computeEffectiveDisplayName(): <{origEffectiveName}>")
    print(f" current computeEffectiveDisplayName():  <{curEffectiveName}>\n")

    for child in xformPrim.GetPrim().GetChildren():
        print(f" {child.GetName()} - {usdex.core.computeEffectiveDisplayName(child)}")


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    createRocket(stage)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sets display names using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
