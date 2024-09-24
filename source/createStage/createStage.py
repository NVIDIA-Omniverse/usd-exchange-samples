# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from pxr import Tf, Usd, UsdGeom, UsdLux


def main(args):
    print(f"Stage path: {args.path}")

    usdex.core.activateDiagnosticsDelegate()
    try:
        # Create/overwrite a USD stage, ensuring that key metadata is set
        # NOTE: UsdGeom.GetFallbackUpAxis() is typically set to UsdGeom.Tokens.y
        stage = usdex.core.createStage(
            identifier=args.path,
            defaultPrimName="World",
            upAxis=UsdGeom.GetFallbackUpAxis(),
            linearUnits=UsdGeom.LinearUnits.centimeters,
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

    # Save the stage to disk
    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a stage using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
