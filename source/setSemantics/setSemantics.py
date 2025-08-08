# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import sys
import traceback

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Sdf, Usd, UsdSemantics


# Construct a house from cubes as children of an Xform prim
def createHouse(stage):
    transform = Gf.Transform()

    validToken = usdex.core.getValidChildName(stage.GetDefaultPrim(), "house")
    transform.SetTranslation(Gf.Vec3d(300, 0, 300))
    xformPrim = usdex.core.defineXform(stage.GetDefaultPrim(), validToken, transform)

    #################################
    # Create wall of house
    #################################
    wall = common.usdUtils.createCube(xformPrim.GetPrim(), "wall")
    # Set the scale
    transform.SetIdentity()
    transform.SetScale(Gf.Vec3d(1, 1, 1))
    usdex.core.setLocalTransform(wall, transform)

    #################################
    # Create roof of house
    #################################
    roof = common.usdUtils.createCube(xformPrim.GetPrim(), "roof")
    # Set the scale
    transform.SetIdentity()
    transform.SetTranslation(Gf.Vec3d(0, 52, 0))
    transform.SetScale(Gf.Vec3d(1.2, 0.05, 1.2))
    usdex.core.setLocalTransform(roof, transform)

    #################################
    # Create door of house
    #################################
    door = common.usdUtils.createCube(xformPrim.GetPrim(), "door")
    # Set the scale
    transform.SetIdentity()
    transform.SetTranslation(Gf.Vec3d(0, -25, -50))
    transform.SetScale(Gf.Vec3d(0.2, 0.5, 0.05))
    usdex.core.setLocalTransform(door, transform)

    #################################
    # Create window of house
    #################################
    window = common.usdUtils.createCube(xformPrim.GetPrim(), "window")
    # Set the scale
    transform.SetIdentity()
    transform.SetTranslation(Gf.Vec3d(0, 0, 50))
    transform.SetScale(Gf.Vec3d(0.3, 0.3, 0.05))
    usdex.core.setLocalTransform(window, transform)

    return xformPrim.GetPath()


# Set Wikidata QCode of a prim
def setQCode(prim, qCodes):
    semAPI = UsdSemantics.LabelsAPI.Apply(prim, "wikidata_qcode")
    semAPI.CreateLabelsAttr(qCodes)


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    housePath = createHouse(stage)

    print(f"Created house prim: {housePath}")

    # Set dense caption (documentation string) to the default prim
    stage.GetDefaultPrim().SetDocumentation(
        "This house was generated using the setSemantics sample, which utilizes Wikidata Q-codes to ensure accurate and consistent semantic representation."
    )

    # Set Q-Codes
    setQCode(stage.GetPrimAtPath(housePath), ["Q3947"])  # https://www.wikidata.org/wiki/Q3947
    setQCode(stage.GetPrimAtPath(housePath.AppendChild("wall")), ["Q42948"])  # https://www.wikidata.org/wiki/Q42948
    setQCode(stage.GetPrimAtPath(housePath.AppendChild("roof")), ["Q83180"])  # https://www.wikidata.org/wiki/Q83180
    setQCode(stage.GetPrimAtPath(housePath.AppendChild("door")), ["Q36794"])  # https://www.wikidata.org/wiki/Q36794
    setQCode(stage.GetPrimAtPath(housePath.AppendChild("window")), ["Q35473"])  # https://www.wikidata.org/wiki/Q35473

    # Iterate through all prims and print prim paths that have semantics
    print(stage.GetDefaultPrim().GetDocumentation())
    for prim in stage.Traverse():
        if prim.HasAPI(UsdSemantics.LabelsAPI):
            query = UsdSemantics.LabelsQuery("wikidata_qcode", Usd.TimeCode.Default())
            print("{} {}".format(prim.GetPath(), query.ComputeUniqueInheritedLabels(prim)))

    # Save the stage to disk
    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sets Q-Code semantic labels and dense captions using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
