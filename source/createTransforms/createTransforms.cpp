// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/gf/transform.h>
#include <pxr/usd/usd/primRange.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdGeom/xformable.h>

#include <iostream>
#include <vector>


//! Find a UsdGeomXformable prim using a simple stage traversal.
//!
//! @param stage A valid stage to traverse
//!
//! @returns A UsdGeomXformable (only valid if found)
pxr::UsdGeomXformable findXformable(pxr::UsdStagePtr stage)
{
    auto range = stage->Traverse();
    for (const auto& node : range)
    {
        if (node.IsA<pxr::UsdGeomXformable>())
        {
            return pxr::UsdGeomXformable(node);
        }
    }
    return pxr::UsdGeomXformable();
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createTransforms", "Create transforms using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Find or create a xformable prim and rotate it using individual components
    pxr::UsdGeomXformable xformable = findXformable(stage);
    if (!xformable)
    {
        xformable = pxr::UsdGeomXformable(samples::createCube(stage->GetDefaultPrim(), "cube"));
    }
    std::cout << "Rotating xformable< " << xformable.GetPrim().GetPath() << "> 45 degrees in the Y axis" << std::endl;

    pxr::GfVec3d position(0);
    pxr::GfVec3d pivot(0);
    pxr::GfVec3f rotation(0);
    usdex::core::RotationOrder rotationOrder;
    pxr::GfVec3f scale(1);
    usdex::core::getLocalTransformComponents(xformable.GetPrim(), position, pivot, rotation, rotationOrder, scale);

    rotation += pxr::GfVec3f(0, 45, 0);
    usdex::core::setLocalTransform(
        xformable.GetPrim(), /* parent prim */
        position, /* translation */
        pivot, /* pivot */
        rotation, /* rotation */
        rotationOrder, /* rotation order */
        scale /* scale */
    );

    // Create a Xform prim with an initial transform
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(stage->GetDefaultPrim(), std::vector<std::string>{ "groundXform" });
    pxr::GfTransform transform;
    transform.SetTranslation(pxr::GfVec3d(0, -55, 0));
    pxr::UsdGeomXform xformPrim = usdex::core::defineXform(stage->GetDefaultPrim(), validTokens[0], transform);

    // Create a "ground plane" cube that is scaled, use the GfMatrix arg to set the transform
    transform = pxr::GfTransform();
    transform.SetScale(pxr::GfVec3d(20, 0.1, 20));
    pxr::UsdGeomCube cube = samples::createCube(xformPrim.GetPrim(), "groundCube");
    usdex::core::setLocalTransform(cube.GetPrim(), transform.GetMatrix());

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
