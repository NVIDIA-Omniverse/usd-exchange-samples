# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys

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
    transform.SetTranslation(Gf.Vec3d(0, 3, 0))
    xformPrim = usdex.core.defineXform(stage.GetDefaultPrim(), validTokens[0], transform)

    #################################
    # Create cylindrical rocket tube
    #################################
    cylinder = common.usdUtils.createCylinder(xformPrim.GetPrim(), "tube")
    # Set the translation
    transform.SetTranslation(Gf.Vec3d(0, 0, 1.5))
    usdex.core.setLocalTransform(cylinder, transform)

    #################################
    # Create nose cone
    #################################
    cone = common.usdUtils.createCone(xformPrim.GetPrim(), "nose")
    # Set the translation
    transform.SetIdentity()
    transform.SetTranslation(Gf.Vec3d(0, 0, 4))
    usdex.core.setLocalTransform(cone, transform)

    #################################
    # Create cube fin 1
    #################################
    fin1 = common.usdUtils.createCube(xformPrim.GetPrim(), "fin")
    # Set the scale
    transform.SetIdentity()
    transform.SetScale(Gf.Vec3d(0.01, 2, 1))
    usdex.core.setLocalTransform(fin1, transform)

    #################################
    # Create cube fin 2
    #################################
    fin2 = common.usdUtils.createCube(xformPrim.GetPrim(), "fin")
    # Set the scale
    transform.SetIdentity()
    transform.SetScale(Gf.Vec3d(2, 0.01, 1))
    usdex.core.setLocalTransform(fin2, transform)

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


def createUniquelyNamedPrims(stage):
    groupName = usdex.core.getValidChildName(stage.GetDefaultPrim(), "uniqueNames")
    groupXform = usdex.core.defineXform(stage.GetDefaultPrim(), groupName)

    preferredNames = ["foo", "foo", "bar", "bar", "foo"]
    primNames = usdex.core.getValidChildNames(groupXform.GetPrim(), preferredNames)

    print("Unique prim names and their authored display names:")
    for primName, preferredName in zip(primNames, preferredNames):
        xformPrim = usdex.core.defineXform(groupXform.GetPrim(), primName)

        # The preferred name is only authored as a display name when uniqueness changed the prim name.
        usdex.core.setEffectiveDisplayName(xformPrim.GetPrim(), preferredName)

        print(f" {xformPrim.GetPrim().GetName()} - <{usdex.core.getDisplayName(xformPrim.GetPrim())}>")


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    createRocket(stage)
    createUniquelyNamedPrims(stage)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sets display names using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
