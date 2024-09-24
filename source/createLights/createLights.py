# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import os
import pathlib
import shutil
import sys

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

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

    rectLightPrim = usdex.core.defineRectLight(parent=stage.GetDefaultPrim(), name=lightPrimNames[0], width=100.0, height=33.0, intensity=5000)

    # Move the light up and rotate it so it shines down onto the stage
    usdex.core.setLocalTransform(
        prim=rectLightPrim.GetPrim(),
        translation=Gf.Vec3d(0.0, 300.0, 0.0),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(-90.0, 0.0, 0.0),  # pointing -z down
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    # Grab the LuxLightAPI so we can set generic light attributes
    lightApi = UsdLux.LightAPI(rectLightPrim)
    lightApi.CreateColorAttr().Set(Gf.Vec3f(0.0, 0.0, 1.0))
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
    # NOTE: Kit/RTX renders domelights with a Z-up axis, rather than Y-up as USDView does
    domeLightPrim = usdex.core.defineDomeLight(parent=stage.GetDefaultPrim(), name=lightPrimNames[0], intensity=0.3, texturePath=texturePath)
    if not domeLightPrim:
        print("Failure to create dome light prim")
        sys.exit(-1)

    # Rotate the dome light if using Kit/RTX for rendering
    # usdex.core.setLocalTransform(
    #    prim=domeLightPrim.GetPrim(),
    #    translation=Gf.Vec3d(0.0),
    #    pivot=Gf.Vec3d(0.0),
    #    rotation=Gf.Vec3f(-90.0, 0.0, 0.0),  # pointing -z down
    #    rotationOrder=usdex.core.RotationOrder.eXyz,
    #    scale=Gf.Vec3f(1),
    # )
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
    relTexturePath = common.sysUtils.copyTextureToStagePath(args.path, "kloofendal_48d_partly_cloudy.hdr")
    createDomeLight(stage, relTexturePath)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates lights using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
