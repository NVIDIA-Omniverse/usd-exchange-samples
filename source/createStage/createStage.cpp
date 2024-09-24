// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/Diagnostics.h>
#include <usdex/core/StageAlgo.h>

#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/boundable.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdLux/distantLight.h>

#include <iostream>


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createStage", "Creates a stage using the OpenUSD Exchange SDK");

    usdex::core::activateDiagnosticsDelegate();

    std::cout << "Stage path: " << args.stagePath << std::endl;

    // Create/overwrite a USD stage, ensuring that key metadata is set
    // NOTE: UsdGeomGetFallbackUpAxis() is typically set to UsdGeomTokens->y
    pxr::UsdStageRefPtr stage = usdex::core::createStage(
        /* identifier */ args.stagePath,
        /* defaultPrimName */ "World",
        /* upAxis */ pxr::UsdGeomGetFallbackUpAxis(),
        /* linearUnits */ pxr::UsdGeomLinearUnits::centimeters,
        /* authoringMetadata */ samples::getSamplesAuthoringMetadata(),
        /* file format args */ args.fileFormatArgs
    );
    if (!stage)
    {
        std::cout << "Error creating stage, exiting" << std::endl;
        return -1;
    }

    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create a 1 meter cube in the stage
    samples::createCube(defaultPrim, "cube");

    // Create a light in the stage (we know this is a new stage so no need to check for valid child names)
    pxr::TfToken validLightToken = pxr::TfToken(usdex::core::getValidPrimName("distantLight"));
    const pxr::SdfPath lightPrimPath = defaultPrim.GetPath().AppendChild(validLightToken);
    pxr::UsdLuxDistantLight light = pxr::UsdLuxDistantLight::Define(stage, lightPrimPath);
    if (!light)
    {
        std::cout << "Error creating distant light, exiting" << std::endl;
        return -1;
    }

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
