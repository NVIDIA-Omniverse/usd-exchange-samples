// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/LightAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/tf/stringUtils.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdLux/domeLight.h>
#include <pxr/usd/usdLux/lightAPI.h>
#include <pxr/usd/usdLux/rectLight.h>

#include <iostream>


//! Create a pxr::UsdLuxRectLight
//!
//! The rect light will be named "rectLight" (or "rectLight_N" if it already exists)
//! The light color, size, intensity, and transform are all hardcoded
//!
//! @param stage The stage to create the rect light
//!
//! @returns The newly created rect light prim
pxr::UsdLuxRectLight createRectLight(pxr::UsdStagePtr stage)
{
    // Get a valid name for the rect light (in case it already exists)
    pxr::TfTokenVector rectLightNames = usdex::core::getValidChildNames(stage->GetDefaultPrim(), std::vector<std::string>{ "rectLight" });

    // Create the rect light
    pxr::UsdLuxRectLight rectLightPrim = usdex::core::defineRectLight(
        stage->GetDefaultPrim(), /* parent prim */
        rectLightNames[0], /* light name */
        100.0f, /* width */
        33.0f, /* height */
        5000.0f /* intensity */
    );

    // Move the light up and rotate it so it shines down onto the stage
    usdex::core::setLocalTransform(
        rectLightPrim.GetPrim(), /* xformable prim */
        pxr::GfVec3d(0.0, 300.0, 0.0), /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(-90.0, 0.0, 0.0), /* rotation - pointing -z down */
        usdex::core::RotationOrder::eXyz,
        pxr::GfVec3f(1.0) /* scale */
    );

    // Grab the LuxLightAPI so we can set generic light attributes
    pxr::UsdLuxLightAPI lightApi = pxr::UsdLuxLightAPI(rectLightPrim);
    lightApi.CreateColorAttr().Set(pxr::GfVec3f(0.0f, 0.0f, 1.0f));

    return rectLightPrim;
}

//! Create a pxr::UsdLuxDomeLight
//!
//! The dome light will be named "domeLight" (or "domeLight_N" if it already exists)
//! The intensity, texturePath, and transform are all set
//!
//! @param stage The stage to create the rect light
//!
//! @returns The newly created rect light prim
pxr::UsdLuxDomeLight createDomeLight(pxr::UsdStagePtr stage, const std::string& texturePath)
{
    // Get a valid name for the dome light (in case it already exists)
    pxr::TfTokenVector domeLightNames = usdex::core::getValidChildNames(stage->GetDefaultPrim(), std::vector<std::string>{ "domeLight" });

    // Create the dome light (note that some renderers have issues with more than one visible domelight)
    // NOTE: Kit/RTX wants a high intensity (1000), USDView likes a low intensity (0.3)
    // NOTE: Kit/RTX renders domelights with a Z-up axis, rather than Y-up as USDView does
    pxr::UsdLuxDomeLight domeLightPrim = usdex::core::defineDomeLight(
        stage->GetDefaultPrim(), /* parent prim */
        domeLightNames[0], /* light name */
        0.3f, /* intensity */
        texturePath.c_str() /* texturePath */
    );

    // Rotate the dome light if using Kit/RTX for rendering
    // usdex::core::setLocalTransform(
    //     domeLightPrim.GetPrim(), /* xformable prim */
    //     pxr::GfVec3d(0.0), /* translation */
    //     pxr::GfVec3d(0.0), /* pivot */
    //     pxr::GfVec3f(-90.0, 0.0, 0.0), /* rotation - pointing -z down */
    //     usdex::core::RotationOrder::eXyz,
    //     pxr::GfVec3f(1.0) /* scale */
    // );

    return domeLightPrim;
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createLights", "Creates lights using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Create a rect light
    createRectLight(stage);

    // Create a textured dome light
    std::string texturePath = samples::copyTextureToStagePath(args.stagePath, "kloofendal_48d_partly_cloudy.hdr");
    createDomeLight(stage, texturePath);

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
