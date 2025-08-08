// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "pxr/base/tf/token.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/Diagnostics.h>
#include <usdex/core/StageAlgo.h>

#include <pxr/usd/usd/primRange.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/boundable.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdSemantics/labelsAPI.h>
#include <pxr/usd/usdSemantics/labelsQuery.h>

#include <iostream>

// wikidata qcode tokens
// clang-format off
PXR_NAMESPACE_USING_DIRECTIVE
TF_DEFINE_PRIVATE_TOKENS(
    wikidataTokens,
    (wikidata_qcode)
    ((house, "Q3947"))  // https://www.wikidata.org/wiki/Q3947
    ((wall, "Q42948"))  // https://www.wikidata.org/wiki/Q42948
    ((roof, "Q83180"))  // https://www.wikidata.org/wiki/Q83180
    ((door, "Q36794"))  // https://www.wikidata.org/wiki/Q36794
    ((window, "Q35473"))// https://www.wikidata.org/wiki/Q35473
);
// clang-format on

// Construct a house from cubes as children of an Xform prim
pxr::SdfPath createHouse(pxr::UsdStageRefPtr stage)
{
    pxr::GfTransform transform;

    // Create Xform prim with an initial transform
    pxr::TfToken validToken = usdex::core::getValidChildName(stage->GetDefaultPrim(), "house");
    transform.SetTranslation(pxr::GfVec3d(300, 0, 300));
    pxr::UsdGeomXform xformPrim = usdex::core::defineXform(stage->GetDefaultPrim(), validToken, transform);

    ///////////////////////////////////
    // Create wall of house
    ///////////////////////////////////
    pxr::UsdGeomCube wall = samples::createCube(xformPrim.GetPrim(), "wall");
    transform.SetIdentity();
    transform.SetScale(pxr::GfVec3d(1, 1, 1));
    usdex::core::setLocalTransform(wall, transform);

    ///////////////////////////////////
    // Create roof of house
    ///////////////////////////////////
    pxr::UsdGeomCube roof = samples::createCube(xformPrim.GetPrim(), "roof");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(0, 52, 0));
    transform.SetScale(pxr::GfVec3d(1.2, 0.05, 1.2));
    usdex::core::setLocalTransform(roof, transform);

    ///////////////////////////////////
    // Create door of house
    ///////////////////////////////////
    pxr::UsdGeomCube door = samples::createCube(xformPrim.GetPrim(), "door");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(0, -25, -50));
    transform.SetScale(pxr::GfVec3d(0.2, 0.5, 0.05));
    usdex::core::setLocalTransform(door, transform);

    ///////////////////////////////////
    // Create window of house
    ///////////////////////////////////
    pxr::UsdGeomCube window = samples::createCube(xformPrim.GetPrim(), "window");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(0, 0, 50));
    transform.SetScale(pxr::GfVec3d(0.3, 0.3, 0.05));
    usdex::core::setLocalTransform(window, transform);

    return xformPrim.GetPath();
}

void setQCode(pxr::UsdPrim prim, const pxr::VtArray<pxr::TfToken>& qCodes)
{
    pxr::UsdSemanticsLabelsAPI semAPI = pxr::UsdSemanticsLabelsAPI::Apply(prim, wikidataTokens->wikidata_qcode);
    semAPI.CreateLabelsAttr(pxr::VtValue(qCodes));
}

int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(
        argc,
        argv,
        "setSemantics",
        "Sets Q-Code semantic labels and dense captions using the OpenUSD Exchange SDK"
    );

    usdex::core::activateDiagnosticsDelegate();

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    pxr::SdfPath housePath = createHouse(stage);

    std::cout << "Created house prim: " << housePath << std::endl;

    // Set dense caption (documentation string) to the default prim
    stage->GetDefaultPrim().SetDocumentation(
        "This house was generated using the setSemantics sample, which utilizes Wikidata Q-codes to ensure accurate and consistent semantic representation."
    );

    // Set Q-Codes
    setQCode(stage->GetPrimAtPath(housePath), { wikidataTokens->house });
    setQCode(stage->GetPrimAtPath(housePath.AppendChild(pxr::TfToken("wall"))), { wikidataTokens->wall });
    setQCode(stage->GetPrimAtPath(housePath.AppendChild(pxr::TfToken("roof"))), { wikidataTokens->roof });
    setQCode(stage->GetPrimAtPath(housePath.AppendChild(pxr::TfToken("door"))), { wikidataTokens->door });
    setQCode(stage->GetPrimAtPath(housePath.AppendChild(pxr::TfToken("window"))), { wikidataTokens->window });

    // Iterate through all prims and print prim paths that have semantics
    std::cout << stage->GetDefaultPrim().GetDocumentation() << std::endl;
    auto range = stage->Traverse();
    for (const auto& prim : range)
    {
        if (prim.HasAPI<pxr::UsdSemanticsLabelsAPI>())
        {
            pxr::UsdSemanticsLabelsQuery query = pxr::UsdSemanticsLabelsQuery(wikidataTokens->wikidata_qcode, pxr::UsdTimeCode::Default());
            std::cout << prim.GetPath() << " " << query.ComputeUniqueInheritedLabels(prim) << std::endl;
        }
    }

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
