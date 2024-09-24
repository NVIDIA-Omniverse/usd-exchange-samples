// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include <usdex/core/XformAlgo.h>

#include <pxr/usd/usd/primRange.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/xformable.h>

#include <iostream>


// The program expects one argument, a path to a USD file
int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        std::cout << "Please provide a local file path to a USD stage to read." << std::endl;
        return -1;
    }

    std::cout << "OpenUSD Stage Traversal: " << argv[1] << std::endl;

    pxr::UsdStageRefPtr stage = pxr::UsdStage::Open(argv[1]);
    if (!stage)
    {
        std::cout << "Failure to open stage.  Exiting." << std::endl;
        return -2;
    }

    // Print the stage metadata metrics
    std::cout << "Stage up-axis: " << pxr::UsdGeomGetStageUpAxis(stage) << std::endl;
    std::cout << "Meters per unit: " << pxr::UsdGeomGetStageMetersPerUnit(stage) << std::endl;

    // Traverse the stage, print all prim names, print transformable prim positions
    pxr::UsdPrimRange range = stage->Traverse();
    for (const auto& prim : range)
    {
        std::cout << prim.GetPath();

        if (pxr::UsdGeomXformable(prim))
        {
            pxr::GfTransform xform = usdex::core::getLocalTransform(prim);
            std::cout << ":" << xform.GetTranslation();
        }
        std::cout << std::endl;
    }
}
