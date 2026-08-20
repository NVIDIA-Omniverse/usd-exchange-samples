# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import os
import pathlib
import shutil
import sys

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Usd, UsdLux


def createRectLight(stage):
    """
    Create a UsdLux.RectLight

    The rect light will be named "rectLight" (or "rectLight_N" if it already exists)
    The light color, size, intensity, and transform are all hardcoded

    Args:
        stage: The stage to create the rect light

    Returns: The newly created rect light prim
    """
    # Get a valid name for the rect light (in case it already exists)
    lightPrimNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["rectLight"])

    rectLightPrim = usdex.core.defineRectLight(parent=stage.GetDefaultPrim(), name=lightPrimNames[0], width=0.25, height=0.25, intensity=500)

    # Move the light up; identity rotation keeps local -Z aimed down the stage up-axis
    usdex.core.setLocalTransform(
        xformable=rectLightPrim,
        translation=Gf.Vec3d(0.0, 0.0, 0.6),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0.0, 0.0, 0.0),  # local -Z points down
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    # Grab the LuxLightAPI so we can set generic light attributes
    lightApi = UsdLux.LightAPI(rectLightPrim)
    lightApi.CreateColorAttr().Set(Gf.Vec3f(0.3, 0.0, 1.0))
    return rectLightPrim


def createDomeLight(stage, texturePath):
    """
    Create a UsdLux.DomeLight

    The dome light will be named "domeLight" (or "domeLight_N" if it already exists)
    The intensity, texturePath, and transform are all set

    Args:
        stage: The stage to create the rect light

    Returns: The newly created rect light prim
    """
    # Get a valid name for the dome light (in case it already exists)
    lightPrimNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["domeLight"])

    # Create the dome light (note that some renderers have issues with more than one visible domelight)
    # NOTE: Kit/RTX wants a high intensity (1000), USDView likes a low intensity (0.3)
    domeLightPrim = usdex.core.defineDomeLight(parent=stage.GetDefaultPrim(), name=lightPrimNames[0], intensity=0.3, texturePath=texturePath)
    if not domeLightPrim:
        print("Failure to create dome light prim")
        sys.exit(-1)

    # Align the dome's default Y-up orientation with the stage up-axis
    domeLightPrim.OrientToStageUpAxis()

    # Preserve the previous 1 km guide size now that each stage unit represents one meter
    domeLightPrim.CreateGuideRadiusAttr(1000.0)

    return domeLightPrim


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    # Create a UsdLux.RectLight
    createRectLight(stage)

    # Create a UsdLux.DomeLight
    relTexturePath = common.sysUtils.copyTextureToStagePath(args.path, "kloofendal_48d_partly_cloudy.exr")
    createDomeLight(stage, relTexturePath)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates lights using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
