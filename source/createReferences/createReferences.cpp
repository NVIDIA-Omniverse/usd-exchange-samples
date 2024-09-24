// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/LayerAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <fmt/format.h>

#include <pxr/base/gf/transform.h>
#include <pxr/usd/usd/payloads.h>
#include <pxr/usd/usd/references.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/xformable.h>

#include <filesystem>
#include <iostream>
#include <vector>


// Create a stage with a 2x2x2 grouping of mesh cubes
std::string createComponentStage(const samples::Args& args)
{
    const char* componentName = "Cube_2x2x2";
    std::filesystem::path stageDir = std::filesystem::path(args.stagePath).parent_path();
    std::filesystem::path extension = std::filesystem::path(args.stagePath).extension();
    std::string stagePath;
    // Make a component stage path that is in the same folder as the root stage path with the same extension
    if (stageDir.empty())
    {
        stagePath = fmt::format("{0}{1}", componentName, extension.string());
    }
    else
    {
        stagePath = fmt::format("{0}/{1}{2}", stageDir.string(), componentName, extension.string());
    }

    // Create a USD component stage in memory, ensuring that key metadata is set
    pxr::UsdStageRefPtr componentStage = pxr::UsdStage::CreateInMemory();
    if (!componentStage)
    {
        return "";
    }

    usdex::core::configureStage(
        /* stage */ componentStage,
        /* defaultPrimName */ componentName,
        /* upAxis */ pxr::UsdGeomGetFallbackUpAxis(),
        /* linearUnits */ pxr::UsdGeomLinearUnits::centimeters,
        /* authoringMetadata*/ samples::getSamplesAuthoringMetadata()
    );

    // Define the defaultPrim as Xform (it was originally created as a Scope)
    pxr::UsdGeomXform xform = usdex::core::defineXform(componentStage, componentStage->GetDefaultPrim().GetPath());

    // Create 8 cubes in a 2x2x2 grid
    float cubeSize = 25.0f;
    double cubeSpacing = 30;
    double offset = -(cubeSize + (cubeSpacing - cubeSize) / 2);
    for (int i = 0; i < 2; i++)
    {
        for (int j = 0; j < 2; j++)
        {
            for (int k = 0; k < 2; k++)
            {
                std::string cubeName = fmt::format("Cube_{0}_{1}_{2}", i, j, k);
                // clang-format off
                pxr::GfVec3d pos(
                    i * (cubeSize + cubeSpacing) + offset,
                    j * (cubeSize + cubeSpacing) + offset,
                    k * (cubeSize + cubeSpacing) + offset
                );
                // clang-format on
                samples::createCubeMesh(componentStage->GetDefaultPrim(), cubeName, cubeSize, pos);
            }
        }
    }

    // Write the component stage to disk
    bool success = usdex::core::exportLayer(
        /* layer */ componentStage->GetRootLayer(),
        /* identifier */ stagePath,
        /* authoringMetadata */ samples::getSamplesAuthoringMetadata(),
        /* comment */ fmt::format("{0} component", componentName).c_str(),
        /* file format args */ args.fileFormatArgs
    );
    if (!success)
    {
        return "";
    }

    return stagePath;
}


// Get the last child prim of a parent prim
pxr::UsdPrim getLastChildPrim(pxr::UsdPrim parent)
{
    pxr::TfTokenVector childNames = parent.GetAllChildrenNames();
    return parent.GetChild(childNames.back());
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createReferences", "Creates a reference and payload using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    std::string componentStagePath = createComponentStage(args);
    if (componentStagePath.empty())
    {
        std::cout << "Error creating component stage, exiting" << std::endl;
        return -1;
    }
    std::cout << "Component stage: " << componentStagePath << std::endl;

    // Make a relative path from the stage's folder to the component's stage. This requires a special case when the stage has no "parent"
    std::string relativeComponentPath;
    std::filesystem::path stageParentPath = std::filesystem::path(args.stagePath).parent_path();
    if (stageParentPath.empty())
    {
        relativeComponentPath = componentStagePath;
    }
    else
    {
        relativeComponentPath = std::filesystem::proximate(componentStagePath, stageParentPath).string();
    }
    std::string referencePath = fmt::format("./{0}", relativeComponentPath);

    // Create a reference prim
    pxr::TfTokenVector primNames = usdex::core::getValidChildNames(defaultPrim, std::vector<std::string>{ "referencePrim" });
    pxr::GfTransform refTransform;
    refTransform.SetTranslation(pxr::GfVec3d(0, 2.5, 300));
    pxr::UsdGeomXform xform = usdex::core::defineXform(defaultPrim, primNames[0], refTransform);
    xform.GetPrim().GetReferences().AddReference(referencePath);
    // Override the mesh scale from the reference
    pxr::UsdGeomXformable xformable = pxr::UsdGeomXformable(getLastChildPrim(xform.GetPrim()));
    if (xformable)
    {
        pxr::GfTransform transform = usdex::core::getLocalTransform(xformable.GetPrim());
        transform.SetScale(pxr::GfVec3d(0.5));
        usdex::core::setLocalTransform(xformable.GetPrim(), transform);
    }

    // Create a payload prim
    primNames = usdex::core::getValidChildNames(defaultPrim, std::vector<std::string>{ "payloadPrim" });
    refTransform.SetTranslation(pxr::GfVec3d(300, 2.5, 0));
    xform = usdex::core::defineXform(defaultPrim, primNames[0], refTransform);
    xform.GetPrim().GetPayloads().AddPayload(referencePath);
    // Override the mesh constant color primvar from the payload
    pxr::UsdGeomMesh mesh = pxr::UsdGeomMesh(getLastChildPrim(xform.GetPrim()));
    if (mesh)
    {
        pxr::VtArray<pxr::GfVec3f> color({ pxr::GfVec3f(0.3f, 0.0f, 1.0f) });
        pxr::UsdGeomPrimvar primvar = mesh.GetDisplayColorPrimvar();
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, color).setPrimvar(primvar);
    }

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
