// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/NameAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/arch/defines.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/cone.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdGeom/cylinder.h>

#include <iostream>


// Construct a rocket of a Cylinder, Cone, and Cubes as children of an Xform prim
// Set their display names at the end to include 🚀
void createRocket(pxr::UsdStageRefPtr stage)
{
    pxr::GfTransform transform;

    // Create Xform prim with an initial transform
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(stage->GetDefaultPrim(), std::vector<std::string>{ "rocket" });
    transform.SetTranslation(pxr::GfVec3d(0, 0, -300));
    pxr::UsdGeomXform xformPrim = usdex::core::defineXform(stage->GetDefaultPrim(), validTokens[0], transform);

    ///////////////////////////////////
    // Create cylindrical rocket tube
    ///////////////////////////////////
    pxr::UsdGeomCylinder cylinder = samples::createCylinder(xformPrim.GetPrim(), "tube");
    transform.SetTranslation(pxr::GfVec3d(0, 150, 0));
    usdex::core::setLocalTransform(cylinder.GetPrim(), transform);

    ///////////////////////////////////
    // Create nose cone
    ///////////////////////////////////
    pxr::UsdGeomCone cone = samples::createCone(xformPrim.GetPrim(), "nose");
    transform.SetTranslation(pxr::GfVec3d(0, 400, 0));
    usdex::core::setLocalTransform(cone.GetPrim(), transform);

    ///////////////////////////////////
    // Create cube fin 1
    ///////////////////////////////////
    pxr::UsdGeomCube fin1 = samples::createCube(xformPrim.GetPrim(), "fin");
    transform.SetIdentity();
    transform.SetScale(pxr::GfVec3d(0.01, 1, 2));
    usdex::core::setLocalTransform(fin1.GetPrim(), transform);

    ///////////////////////////////////
    // Create cube fin 2
    ///////////////////////////////////
    pxr::UsdGeomCube fin2 = samples::createCube(xformPrim.GetPrim(), "fin");
    transform.SetIdentity();
    transform.SetScale(pxr::GfVec3d(2, 1, 0.01));
    usdex::core::setLocalTransform(fin2.GetPrim(), transform);

    ///////////////////////////////////
    // Access prim display names
    ///////////////////////////////////
    std::string origDisplayName = usdex::core::getDisplayName(xformPrim.GetPrim());
    std::string origEffectiveName = usdex::core::computeEffectiveDisplayName(xformPrim.GetPrim());

    ///////////////////////////////////
    // Apply prim display names
    ///////////////////////////////////
    usdex::core::setDisplayName(xformPrim.GetPrim(), "🚀");
    usdex::core::setDisplayName(cylinder.GetPrim(), "⛽ tube");
    usdex::core::setDisplayName(cone.GetPrim(), "👃 nose");
    usdex::core::setDisplayName(fin1.GetPrim(), "🦈 fin");
    usdex::core::setDisplayName(fin2.GetPrim(), "🦈 fin");

    /////////////////////////////////////////////////
    // Access and report updated prim display names
    /////////////////////////////////////////////////
    std::string curEffectiveName = usdex::core::computeEffectiveDisplayName(xformPrim.GetPrim());
    std::cout << "Xform prim display name status:" << std::endl;
    std::cout << " original getDisplayName():              <" << origDisplayName << ">" << std::endl;
    std::cout << " original computeEffectiveDisplayName(): <" << origEffectiveName << ">" << std::endl;
    std::cout << " current computeEffectiveDisplayName():  <" << curEffectiveName << ">" << std::endl;
}


int main(int argc, char* argv[])
{
#ifdef ARCH_OS_WINDOWS
    // Set console code page to UTF-8 so console can output the 🚀
    SetConsoleOutputCP(CP_UTF8);
#endif

    samples::Args args = samples::parseCommonOptions(argc, argv, "setDisplayNames", "Sets display names using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Make a multi-shape 🚀
    createRocket(stage);

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
