# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys
import traceback

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Tf, Usd, UsdGeom, UsdLux


def main(args):
    print(f"Stage path: {args.path}")

    usdex.core.activateDiagnosticsDelegate()
    try:
        # Create/overwrite a USD stage, ensuring that key metadata is set
        # NOTE: Samples use Z-up (UsdGeom.Tokens.z)
        stage = usdex.core.createStage(
            identifier=args.path,
            defaultPrimName="World",
            upAxis=UsdGeom.Tokens.z,
            linearUnits=UsdGeom.LinearUnits.meters,
            authoringMetadata=common.usdUtils.getSamplesAuthoringMetadata(),
            fileFormatArgs=args.fileFormatArgs,
        )
        if not stage:
            print("Error creating stage, exiting")
            sys.exit(-1)

    except Tf.ErrorException:
        print(traceback.format_exc())
        print("Error creating stage, exiting")
        sys.exit(-1)

    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create a 1 meter cube in the stage
    common.usdUtils.createCube(defaultPrim, "cube")

    # Create a light in the stage (we know this is a new stage so no need to check for valid child names)
    validLightToken = usdex.core.getValidPrimName("distantLight")
    lightPrimPath = defaultPrim.GetPath().AppendChild(validLightToken)
    light = UsdLux.DistantLight.Define(stage, lightPrimPath)
    if not light:
        print("Error creating distant light, exiting")
        sys.exit(-1)

    # Set the light intensity to 1000
    light.CreateIntensityAttr().Set(1000.0)

    # Tilt the light down and to the side
    usdex.core.setLocalTransform(
        xformable=light,
        translation=Gf.Vec3d(0.0),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(20.0, 0.0, 10.0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1.0),
    )

    # Save the stage to disk
    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a stage using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
