// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/AssetStructure.h>
#include <usdex/core/Core.h>
#include <usdex/core/LayerAlgo.h>
#include <usdex/core/MaterialAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/gf/transform.h>
#include <pxr/base/tf/stringUtils.h>
#include <pxr/usd/kind/registry.h>
#include <pxr/usd/usd/modelAPI.h>
#include <pxr/usd/usd/payloads.h>
#include <pxr/usd/usd/references.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/xformable.h>
#include <pxr/usd/usdShade/material.h>

#include <filesystem>
#include <iostream>
#include <vector>


// Create an atomic component asset for a flower planter with 3 flowers
pxr::UsdStageRefPtr createAsset(const samples::Args& args)
{
    const char* componentStageName = "FlowerPlanter.usda";
    std::filesystem::path stageDir = std::filesystem::path(args.stagePath).parent_path();
    std::filesystem::path stagePath = stageDir / componentStageName;

    // Create the main asset stage with proper metadata and default prim
    pxr::UsdStageRefPtr assetStage = usdex::core::createStage(
        stagePath.string(),
        "FlowerPlanter",
        pxr::UsdGeomGetFallbackUpAxis(),
        pxr::UsdGeomLinearUnits::centimeters,
        samples::getSamplesAuthoringMetadata()
    );
    if (!assetStage)
    {
        return nullptr;
    }

    // Create a transform for the default prim and set its display name
    pxr::UsdGeomXform assetXform = usdex::core::defineXform(assetStage, assetStage->GetDefaultPrim().GetPath());
    usdex::core::setDisplayName(assetXform.GetPrim(), "🌻");

    // Create a payload stage to hold the asset's content
    pxr::UsdStageRefPtr payloadStage = usdex::core::createAssetPayload(assetStage);
    if (!payloadStage)
    {
        return nullptr;
    }

    // Create a geometry library to store reusable mesh definitions
    pxr::UsdStageRefPtr geometryLibraryStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getGeometryToken());

    // Define the basic geometric shapes for our flower components
    pxr::UsdGeomCylinder planterLibraryGeom = samples::createCylinder(
        geometryLibraryStage->GetDefaultPrim(),
        "Planter",
        pxr::UsdGeomGetFallbackUpAxis(),
        10.0f,
        15.0f // Larger planter for 3 flowers
    );
    pxr::UsdGeomCylinder
        stemLibraryGeom = samples::createCylinder(geometryLibraryStage->GetDefaultPrim(), "Stem", pxr::UsdGeomGetFallbackUpAxis(), 20.0f, 1.0f);
    pxr::UsdGeomCylinder
        petalLibraryGeom = samples::createCylinder(geometryLibraryStage->GetDefaultPrim(), "Petal", pxr::UsdGeomGetFallbackUpAxis(), 2.5f, 8.0f);

    // Create a materials library to store reusable material definitions
    pxr::UsdStageRefPtr materialsLibraryStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getMaterialsToken());

    // Define materials with appropriate colors for each component
    pxr::UsdShadeMaterial clayLibraryMat = usdex::core::definePreviewMaterial(
        materialsLibraryStage->GetDefaultPrim(),
        "Clay",
        pxr::GfVec3f(0.7f, 0.44f, 0.24f)
    );
    pxr::UsdShadeMaterial greenStemLibraryMat = usdex::core::definePreviewMaterial(
        materialsLibraryStage->GetDefaultPrim(),
        "GreenStem",
        pxr::GfVec3f(0.0f, 1.0f, 0.0f)
    );
    pxr::UsdShadeMaterial yellowPetalsLibraryMat = usdex::core::definePreviewMaterial(
        materialsLibraryStage->GetDefaultPrim(),
        "YellowPetals",
        pxr::GfVec3f(1.0f, 0.85f, 0.1f)
    );

    // Create geometry content layer with positioned instances of our library meshes
    pxr::UsdStageRefPtr geometryStage = usdex::core::addAssetContent(payloadStage, usdex::core::getGeometryToken());
    pxr::SdfPath geomScopePath = geometryStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getGeometryToken());
    pxr::UsdPrim geomScope = geometryStage->GetPrimAtPath(geomScopePath);

    // Create a hierarchical structure for the flower planter components using Xform nodes
    pxr::UsdGeomXform flowerPlanterXform = usdex::core::defineXform(geomScope, "FlowerPlanterStructure");

    // Single planter at the base (shared by all flowers)
    pxr::UsdPrim planterRef = usdex::core::defineReference(flowerPlanterXform.GetPrim(), planterLibraryGeom.GetPrim());
    usdex::core::setLocalTransform(
        planterRef,
        pxr::GfVec3d(0, 5, 0), // Position planter at ground level
        pxr::GfVec3d(0.0),
        pxr::GfVec3f(0, 0, 0),
        usdex::core::RotationOrder::eXyz,
        pxr::GfVec3f(1)
    );

    const int numFlowers = 3;

    // Create a vector of flower names
    pxr::TfTokenVector flowerNames = usdex::core::getValidChildNames(flowerPlanterXform.GetPrim(), { "Flower", "Flower", "Flower" });

    // Create 3 flowers with different positions
    std::vector<pxr::GfVec3d> flowerPositions = {
        pxr::GfVec3d(-8, 0, 0), // Left flower
        pxr::GfVec3d(0, 0, 0), // Center flower
        pxr::GfVec3d(8, 0, 0), // Right flower
    };

    std::vector<pxr::GfVec3f> flowerRotation = {
        pxr::GfVec3f(0, 0, 30),
        pxr::GfVec3f(0, 0, 0),
        pxr::GfVec3f(0, 0, -30),
    };

    for (size_t i = 0; i < numFlowers; ++i)
    {
        std::string flowerName = flowerNames[i].GetString();

        // Create Xform for each flower's stem positioning
        pxr::UsdGeomXform flowerXform = usdex::core::defineXform(flowerPlanterXform.GetPrim(), flowerName);

        pxr::UsdGeomXform stemXform = usdex::core::defineXform(flowerXform.GetPrim(), "StemXform");
        usdex::core::setLocalTransform(
            stemXform.GetPrim(),
            pxr::GfVec3d(flowerPositions[i][0], 15, flowerPositions[i][2]), // Position stem relative to planter top
            pxr::GfVec3d(0.0),
            flowerRotation[i],
            usdex::core::RotationOrder::eXyz,
            pxr::GfVec3f(1)
        );

        // Stem positioned relative to planter
        usdex::core::defineReference(stemXform.GetPrim(), stemLibraryGeom.GetPrim());

        // Create Xform for petals positioning
        pxr::UsdGeomXform petalXform = usdex::core::defineXform(stemXform.GetPrim(), "PetalXform");
        usdex::core::setLocalTransform(
            petalXform.GetPrim(),
            pxr::GfVec3d(0, 10, 0), // Position petals relative to stem top
            pxr::GfVec3d(0.0),
            pxr::GfVec3f(90, 0, 0), // Rotate petals to face outward
            usdex::core::RotationOrder::eXyz,
            pxr::GfVec3f(1)
        );

        // Petals positioned relative to stem
        usdex::core::defineReference(petalXform.GetPrim(), petalLibraryGeom.GetPrim());
    }

    // Create materials content layer and bind materials to geometry
    pxr::UsdStageRefPtr materialsStage = usdex::core::addAssetContent(payloadStage, usdex::core::getMaterialsToken());
    pxr::SdfPath materialScopePath = materialsStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getMaterialsToken());
    pxr::UsdPrim materialsScope = materialsStage->GetPrimAtPath(materialScopePath);

    // Create material references from our library
    pxr::UsdPrim clayRef = usdex::core::defineReference(materialsScope, clayLibraryMat.GetPrim());
    pxr::UsdPrim greenStemRef = usdex::core::defineReference(materialsScope, greenStemLibraryMat.GetPrim());
    pxr::UsdPrim yellowPetalsRef = usdex::core::defineReference(materialsScope, yellowPetalsLibraryMat.GetPrim());

    // Apply materials to the appropriate geometric components
    pxr::UsdPrim planterOverrides = materialsStage->OverridePrim(planterRef.GetPath());
    usdex::core::bindMaterial(planterOverrides, pxr::UsdShadeMaterial(clayRef));

    pxr::SdfPath flowerPlanterStructurePath = geomScopePath.AppendChild(pxr::TfToken("FlowerPlanterStructure"));
    // Apply materials to all stems and petals
    for (size_t i = 0; i < numFlowers; ++i)
    {
        std::string flowerName = flowerNames[i].GetString();
        pxr::SdfPath flowerXformPath = flowerPlanterStructurePath.AppendChild(pxr::TfToken(flowerName));
        pxr::SdfPath stemXformPath = flowerXformPath.AppendChild(pxr::TfToken("StemXform"));
        pxr::SdfPath petalXformPath = stemXformPath.AppendChild(pxr::TfToken("PetalXform"));
        pxr::SdfPath stemPath = stemXformPath.AppendChild(pxr::TfToken("Stem"));
        pxr::SdfPath petalPath = petalXformPath.AppendChild(pxr::TfToken("Petal"));

        pxr::UsdPrim stemOverrides = materialsStage->OverridePrim(stemPath);
        pxr::UsdPrim petalOverrides = materialsStage->OverridePrim(petalPath);

        if (stemOverrides)
        {
            usdex::core::bindMaterial(stemOverrides, pxr::UsdShadeMaterial(greenStemRef));
        }
        if (petalOverrides)
        {
            usdex::core::bindMaterial(petalOverrides, pxr::UsdShadeMaterial(yellowPetalsRef));
        }
    }

    // Connect the payload stage to the main asset stage
    usdex::core::addAssetInterface(assetStage, payloadStage);
    if (!assetStage)
    {
        return nullptr;
    }

    return assetStage;
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createAsset", "Creates an atomic model asset using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Set the World prim to assembly kind to allow component children
    pxr::UsdModelAPI(defaultPrim).SetKind(pxr::KindTokens->assembly);

    pxr::UsdStageRefPtr assetStage = createAsset(args);
    if (!assetStage)
    {
        std::cout << "Error creating asset stage, exiting" << std::endl;
        return -1;
    }

    std::cout << "Asset stage: " << assetStage->GetRootLayer()->GetIdentifier() << std::endl;

    // Create a reference to the asset
    pxr::GfTransform refTransform;
    refTransform.SetTranslation(pxr::GfVec3d(-300, -50, 300));
    refTransform.SetScale(pxr::GfVec3d(5));

    pxr::UsdPrim prim = usdex::core::defineReference(defaultPrim, assetStage->GetDefaultPrim(), "FlowerPlanter");
    pxr::UsdGeomXform xform(prim);
    usdex::core::setLocalTransform(xform, refTransform);

    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
