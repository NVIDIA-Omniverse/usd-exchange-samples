// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/AssetStructure.h>
#include <usdex/core/Core.h>
#include <usdex/core/LayerAlgo.h>
#include <usdex/core/MaterialAlgo.h>
#include <usdex/core/PrimvarData.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/gf/transform.h>
#include <pxr/usd/kind/registry.h>
#include <pxr/usd/usd/attribute.h>
#include <pxr/usd/usd/modelAPI.h>
#include <pxr/usd/usd/payloads.h>
#include <pxr/usd/usd/references.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/primvar.h>
#include <pxr/usd/usdGeom/primvarsAPI.h>
#include <pxr/usd/usdGeom/scope.h>
#include <pxr/usd/usdGeom/tokens.h>
#include <pxr/usd/usdGeom/xformable.h>
#include <pxr/usd/usdShade/material.h>

#include <cmath>
#include <filesystem>
#include <iostream>
#include <vector>

// Internal tokens
// clang-format off
PXR_NAMESPACE_USING_DIRECTIVE
TF_DEFINE_PRIVATE_TOKENS(
    sampleTokens,
    (diffuseColor)
    (bodyPaintColor)
    (Classes)
);
// clang-format on

// All constants in one organized struct
struct Constants
{
    // Car component constants
    static constexpr pxr::GfVec3d carDims{ 0.178, 0.0318, 0.0445 }; // length, height, width in m
    static constexpr pxr::GfVec3f carBodyColor{ 1, 0, 0 }; // red
    static constexpr pxr::GfVec3f lightBlue{ 0.3284f, 0.7490f, 0.7098f }; // light blue
    static constexpr pxr::GfVec3f green{ 0.294f, 0.725f, 0.0f }; // green

    // Axle constants
    static constexpr double axleLength = 0.0254;
    static constexpr double axleRadius = 0.0011;
    static constexpr double axleHeadRadius = 0.003;
    static constexpr double axleHeadLength = 0.001;
    static constexpr pxr::GfVec3f axleColor{ 0.5f, 0.5f, 0.75f };
    static constexpr double axleRearOffset = 0.02;
    static constexpr double axleFrontOffset = 0.0508;

    // Wheel constants
    static constexpr double wheelRadius = 0.015;
    static constexpr double wheelWidth = 0.01;
    static constexpr pxr::GfVec3f wheelColor{ 0, 0, 0 }; // black

    // Track component constants
    static constexpr pxr::GfVec3d trackDims{ 4, 1, 0.5 }; // length, height, width in m
    static constexpr pxr::GfVec3f trackRampColor{ 0.6f, 0.4f, 0.2f }; // brown
    // Calculated constants
    static constexpr double trackAngle = 14.0362434679264787; // height/length in degrees (precalculated: std::atan(100/400) * 180.0 / M_PI)
    static const double trackDividerLength; // Calculated in source file
};

// Define the calculated constant
const double Constants::trackDividerLength = std::hypot(Constants::trackDims[0], Constants::trackDims[1]);


// Create an atomic component asset for a pinewood derby car
pxr::UsdStageRefPtr createCarComponent(const samples::Args& args)
{
    const std::string componentName = "PinewoodDerbyCar";
    const std::string componentStageName = componentName + ".usda";
    std::filesystem::path stageDir = std::filesystem::path(args.stagePath).parent_path();
    std::filesystem::path stagePath = stageDir / componentName / componentStageName;

    // This is really for instructional purposes, in production asset libraries should be binary
    std::string libraryExtension = std::filesystem::path(args.stagePath).extension().string().substr(1);

    // Create the main asset stage with proper metadata and default prim
    pxr::UsdStageRefPtr assetStage = usdex::core::createStage(
        stagePath.string(),
        componentName,
        pxr::UsdGeomTokens->z,
        pxr::UsdGeomLinearUnits::meters,
        samples::getSamplesAuthoringMetadata()
    );
    if (!assetStage)
    {
        return nullptr;
    }

    // Create a transform for the default prim
    pxr::UsdGeomXform assetXform = usdex::core::defineXform(assetStage, assetStage->GetDefaultPrim().GetPath());

    // Create a payload stage to hold the asset's content
    pxr::UsdStageRefPtr payloadStage = usdex::core::createAssetPayload(assetStage);
    if (!payloadStage)
    {
        return nullptr;
    }

    // Create a geometry library to store reusable mesh definitions
    pxr::UsdStageRefPtr geometryLibraryStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getGeometryToken(), libraryExtension);

    // Create car body mesh
    pxr::UsdGeomMesh bodyMesh = samples::createWedge(
        geometryLibraryStage->GetDefaultPrim(),
        "body",
        static_cast<float>(Constants::carDims[1]), // height
        static_cast<float>(Constants::carDims[0]), // length
        static_cast<float>(Constants::carDims[2]) // width
    );

    // Create a materials library to store reusable material definitions
    pxr::UsdStageRefPtr materialsLibStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getMaterialsToken(), libraryExtension);

    // Define materials with appropriate colors for each component
    pxr::UsdShadeMaterial bodyMat = usdex::core::definePreviewMaterial(
        materialsLibStage->GetDefaultPrim(),
        "body",
        Constants::carBodyColor,
        1.0f, // opacity
        0.15f, // roughness
        0.0f // metallic
    );

    // Create primvar reader for the body paint color
    usdex::core::addPrimvarShaderToPreviewMaterial(bodyMat, sampleTokens->diffuseColor, sampleTokens->bodyPaintColor);

    pxr::UsdShadeMaterial axleMat = usdex::core::definePreviewMaterial(
        materialsLibStage->GetDefaultPrim(),
        "shinyAxle",
        Constants::axleColor,
        1.0f, // opacity
        0.0f, // roughness
        1.0f // metallic
    );
    pxr::UsdShadeMaterial tireMat = usdex::core::definePreviewMaterial(
        materialsLibStage->GetDefaultPrim(),
        "tire",
        Constants::wheelColor,
        1.0f, // opacity
        1.0f, // roughness
        0.0f // metallic
    );

    // Create geometry content layer with positioned instances of our library meshes
    pxr::UsdStageRefPtr geometryStage = usdex::core::addAssetContent(payloadStage, usdex::core::getGeometryToken());
    pxr::SdfPath geomScopePath = geometryStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getGeometryToken());
    pxr::UsdPrim geomScope = geometryStage->GetPrimAtPath(geomScopePath);

    // The car is offset by the wheel radius and the axle radius to ensure the wheels are on the ground when the carXform is on the ground
    pxr::GfTransform transform;
    transform.SetTranslation(pxr::GfVec3d(0, 0, Constants::wheelRadius - Constants::axleRadius * 2));
    pxr::UsdGeomXform carXform = usdex::core::defineXform(geomScope, "pinewoodCar", transform);
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(0, 0, Constants::carDims[1] * 0.5));
    pxr::UsdGeomXform bodyXform = usdex::core::defineXform(carXform.GetPrim(), "bodyOffset", transform);
    pxr::UsdPrim bodyMeshRef = usdex::core::defineReference(bodyXform.GetPrim(), bodyMesh.GetPrim());

    // Add a class definition for the wheel-axle subcomponent
    pxr::UsdGeomScope classesScope = usdex::core::defineScope(geometryStage->GetPseudoRoot(), sampleTokens->Classes);
    classesScope.GetPrim().SetSpecifier(pxr::SdfSpecifierClass);

    // Make a wheel-axle subcomponent
    transform.SetIdentity();
    pxr::UsdGeomXform wheelAxleXform = usdex::core::defineXform(classesScope.GetPrim(), "wheelAxle", transform);
    pxr::UsdModelAPI(wheelAxleXform.GetPrim()).SetKind(pxr::KindTokens->subcomponent);

    pxr::UsdGeomCylinder axleShaft = samples::createCylinder(
        wheelAxleXform.GetPrim(),
        "axleShaft",
        pxr::UsdGeomTokens->y,
        Constants::axleLength,
        Constants::axleRadius,
        std::nullopt,
        std::nullopt,
        std::nullopt,
        Constants::axleColor
    );
    pxr::UsdGeomCylinder axleHead = samples::createCylinder(
        wheelAxleXform.GetPrim(),
        "axleHead",
        pxr::UsdGeomTokens->y,
        Constants::axleHeadLength,
        Constants::axleHeadRadius,
        pxr::GfVec3d(0, Constants::axleLength * 0.5, 0),
        std::nullopt,
        std::nullopt,
        Constants::axleColor
    );
    pxr::UsdGeomCylinder wheel = samples::createCylinder(
        wheelAxleXform.GetPrim(),
        "wheel",
        pxr::UsdGeomTokens->y,
        Constants::wheelWidth,
        Constants::wheelRadius,
        pxr::GfVec3d(0, Constants::wheelWidth * 0.65, 0),
        std::nullopt,
        std::nullopt,
        Constants::wheelColor
    );

    // Left front axle
    pxr::UsdPrim axleXform = usdex::core::defineReference(bodyXform.GetPrim(), wheelAxleXform.GetPrim(), "axleLeftFront");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(
        Constants::carDims[0] * 0.5 - Constants::axleFrontOffset,
        Constants::carDims[2] * 0.5,
        -Constants::carDims[1] * 0.5 + Constants::axleRadius * 2
    ));
    usdex::core::setLocalTransform(axleXform, transform);

    // Right front axle
    axleXform = usdex::core::defineReference(bodyXform.GetPrim(), wheelAxleXform.GetPrim(), "axleRightFront");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(
        Constants::carDims[0] * 0.5 - Constants::axleFrontOffset,
        -Constants::carDims[2] * 0.5,
        -Constants::carDims[1] * 0.5 + Constants::axleRadius * 2
    ));
    transform.SetRotation(pxr::GfRotation(pxr::GfVec3d(0, 0, 1), -180));
    usdex::core::setLocalTransform(axleXform, transform);

    // Left rear axle
    axleXform = usdex::core::defineReference(bodyXform.GetPrim(), wheelAxleXform.GetPrim(), "axleLeftRear");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(
        -Constants::carDims[0] * 0.5 + Constants::axleRearOffset,
        Constants::carDims[2] * 0.5,
        -Constants::carDims[1] * 0.5 + Constants::axleRadius * 2
    ));
    usdex::core::setLocalTransform(axleXform, transform);

    // Right rear axle
    axleXform = usdex::core::defineReference(bodyXform.GetPrim(), wheelAxleXform.GetPrim(), "axleRightRear");
    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(
        -Constants::carDims[0] * 0.5 + Constants::axleRearOffset,
        -Constants::carDims[2] * 0.5,
        -Constants::carDims[1] * 0.5 + Constants::axleRadius * 2
    ));
    transform.SetRotation(pxr::GfRotation(pxr::GfVec3d(0, 0, 1), -180));
    usdex::core::setLocalTransform(axleXform, transform);

    // Create materials content layer and bind materials to geometry
    pxr::UsdStageRefPtr materialsStage = usdex::core::addAssetContent(payloadStage, usdex::core::getMaterialsToken());
    pxr::SdfPath materialScopePath = materialsStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getMaterialsToken());
    pxr::UsdPrim materialsScope = materialsStage->GetPrimAtPath(materialScopePath);

    // Create material references from our library
    pxr::UsdPrim bodyMatRef = usdex::core::defineReference(materialsScope, bodyMat.GetPrim());
    pxr::UsdPrim axleMatRef = usdex::core::defineReference(materialsScope, axleMat.GetPrim());
    pxr::UsdPrim tireMatRef = usdex::core::defineReference(materialsScope, tireMat.GetPrim());

    // Apply materials to the appropriate geometric components
    pxr::UsdPrim bodyOverrides = materialsStage->OverridePrim(bodyMeshRef.GetPath());
    usdex::core::bindMaterial(bodyOverrides, pxr::UsdShadeMaterial(bodyMatRef));

    pxr::UsdPrim axleShaftOverrides = materialsStage->OverridePrim(axleShaft.GetPrim().GetPath());
    usdex::core::bindMaterial(axleShaftOverrides, pxr::UsdShadeMaterial(axleMatRef));

    pxr::UsdPrim axleHeadOverrides = materialsStage->OverridePrim(axleHead.GetPrim().GetPath());
    usdex::core::bindMaterial(axleHeadOverrides, pxr::UsdShadeMaterial(axleMatRef));

    pxr::UsdPrim wheelOverrides = materialsStage->OverridePrim(wheel.GetPrim().GetPath());
    usdex::core::bindMaterial(wheelOverrides, pxr::UsdShadeMaterial(tireMatRef));

    // Connect the payload stage to the main asset stage
    usdex::core::addAssetInterface(assetStage, payloadStage);
    if (!assetStage)
    {
        return nullptr;
    }

    // Add asset parameterization interface, the car body paint color using a primvar (defaults to red)
    UsdPrim prim = assetXform.GetPrim();
    pxr::UsdGeomPrimvar primvar;
    primvar = usdex::core::createConstantPrimvar(prim, sampleTokens->bodyPaintColor, Constants::carBodyColor, pxr::SdfValueTypeNames->Color3f);
    if (!primvar)
    {
        std::cout << "Error creating body paint color primvar" << std::endl;
        return nullptr;
    }

    primvar.GetAttr().SetDisplayName("Car Body Paint Color");

    return assetStage;
}


// Create a track component asset for a pinewood derby track
pxr::UsdStageRefPtr createTrackComponent(const samples::Args& args)
{
    const std::string componentName = "PinewoodDerbyTrack";
    const std::string componentStageName = componentName + ".usda";
    std::filesystem::path stageDir = std::filesystem::path(args.stagePath).parent_path();
    std::filesystem::path stagePath = stageDir / componentName / componentStageName;

    // This is really for instructional purposes, in production asset libraries should be binary
    std::string libraryExtension = std::filesystem::path(args.stagePath).extension().string().substr(1);

    // Create the main asset stage with proper metadata and default prim
    pxr::UsdStageRefPtr assetStage = usdex::core::createStage(
        stagePath.string(),
        componentName,
        pxr::UsdGeomTokens->z,
        pxr::UsdGeomLinearUnits::meters,
        samples::getSamplesAuthoringMetadata()
    );
    if (!assetStage)
    {
        return nullptr;
    }

    // Create a transform for the default prim
    pxr::UsdGeomXform assetXform = usdex::core::defineXform(assetStage, assetStage->GetDefaultPrim().GetPath());

    // Create a payload stage to hold the asset's content
    pxr::UsdStageRefPtr payloadStage = usdex::core::createAssetPayload(assetStage);
    if (!payloadStage)
    {
        return nullptr;
    }

    // Create a geometry library to store reusable mesh definitions (usda format for instructional purposes)
    pxr::UsdStageRefPtr geometryLibraryStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getGeometryToken(), libraryExtension);

    // Create track geometry using global constants
    pxr::UsdGeomMesh rampMesh = samples::createWedge(
        geometryLibraryStage->GetDefaultPrim(),
        "ramp",
        static_cast<float>(Constants::trackDims[1]), // height
        static_cast<float>(Constants::trackDims[0]), // length
        static_cast<float>(Constants::trackDims[2]) // width
    );

    // Create a materials library to store reusable material definitions (usda format for instructional purposes)
    pxr::UsdStageRefPtr materialsLibraryStage = usdex::core::addAssetLibrary(payloadStage, usdex::core::getMaterialsToken(), libraryExtension);

    // Define materials with appropriate colors for each component
    pxr::UsdShadeMaterial rampMat = usdex::core::definePreviewMaterial(
        materialsLibraryStage->GetDefaultPrim(),
        "ramp",
        Constants::trackRampColor,
        1.0f, // opacity
        0.15f, // roughness
        0.0f // metallic
    );

    // Create geometry content layer with positioned instances of our library meshes
    pxr::UsdStageRefPtr geometryStage = usdex::core::addAssetContent(payloadStage, usdex::core::getGeometryToken());
    pxr::SdfPath geomScopePath = geometryStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getGeometryToken());
    pxr::UsdPrim geomScope = geometryStage->GetPrimAtPath(geomScopePath);

    pxr::UsdPrim rampRef = usdex::core::defineReference(geomScope, rampMesh.GetPrim());
    pxr::GfTransform transform = usdex::core::getLocalTransform(rampRef);
    transform.SetTranslation(pxr::GfVec3d(0, 0, Constants::trackDims[1] * 0.5));
    usdex::core::setLocalTransform(rampRef, transform);

    std::vector<pxr::UsdGeomCube> dividers;
    dividers.push_back(samples::createCube(
        geomScope,
        "divider",
        1.0,
        pxr::GfVec3d(0, 0, Constants::trackDims[1] * 0.5),
        pxr::GfVec3f(0, static_cast<float>(Constants::trackAngle), 0),
        pxr::GfVec3f(static_cast<float>(Constants::trackDividerLength), 0.02f, 0.04f)
    ));
    dividers.push_back(samples::createCube(
        geomScope,
        "divider",
        1.0,
        pxr::GfVec3d(0, Constants::trackDims[2] * 0.5 - 0.011, Constants::trackDims[1] * 0.5),
        pxr::GfVec3f(0, static_cast<float>(Constants::trackAngle), 0),
        pxr::GfVec3f(static_cast<float>(Constants::trackDividerLength), 0.02f, 0.04f)
    ));
    dividers.push_back(samples::createCube(
        geomScope,
        "divider",
        1.0,
        pxr::GfVec3d(0, -Constants::trackDims[2] * 0.5 + 0.011, Constants::trackDims[1] * 0.5),
        pxr::GfVec3f(0, static_cast<float>(Constants::trackAngle), 0),
        pxr::GfVec3f(static_cast<float>(Constants::trackDividerLength), 0.02f, 0.04f)
    ));

    // Create materials content layer and bind materials to geometry
    pxr::UsdStageRefPtr materialsStage = usdex::core::addAssetContent(payloadStage, usdex::core::getMaterialsToken());
    pxr::SdfPath materialScopePath = materialsStage->GetDefaultPrim().GetPath().AppendChild(usdex::core::getMaterialsToken());
    pxr::UsdPrim materialsScope = materialsStage->GetPrimAtPath(materialScopePath);

    // Create material references from our library
    pxr::UsdPrim rampMatRef = usdex::core::defineReference(materialsScope, rampMat.GetPrim());

    // Apply materials to the appropriate geometric components
    pxr::UsdPrim rampOverrides = materialsStage->OverridePrim(rampRef.GetPath());
    usdex::core::bindMaterial(rampOverrides, pxr::UsdShadeMaterial(rampMatRef));

    for (const auto& divider : dividers)
    {
        pxr::UsdPrim dividerOverrides = materialsStage->OverridePrim(divider.GetPath());
        usdex::core::bindMaterial(dividerOverrides, pxr::UsdShadeMaterial(rampMatRef));
    }

    // Connect the payload stage to the main asset stage
    usdex::core::addAssetInterface(assetStage, payloadStage);
    if (!assetStage)
    {
        return nullptr;
    }

    return assetStage;
}

bool createPinewoodDerbyAssembly(pxr::UsdStageRefPtr stage, pxr::UsdStageRefPtr trackComponentStage, pxr::UsdStageRefPtr carComponentStage)
{
    pxr::GfTransform transform;
    transform.SetTranslation(pxr::GfVec3d(4, -6, -0.5));
    pxr::UsdGeomXform pinewoodDerbyAssembly = usdex::core::defineXform(stage->GetDefaultPrim(), "PinewoodDerbyAssembly", transform);

    usdex::core::defineReference(pinewoodDerbyAssembly.GetPrim(), trackComponentStage->GetDefaultPrim(), "Track");

    pxr::UsdPrim car0Prim = usdex::core::defineReference(pinewoodDerbyAssembly.GetPrim(), carComponentStage->GetDefaultPrim(), "BlueCar");
    bool success = usdex::core::setConstantPrimvar(car0Prim.GetPrim(), sampleTokens->bodyPaintColor, Constants::lightBlue);

    pxr::UsdPrim car1Prim = usdex::core::defineReference(pinewoodDerbyAssembly.GetPrim(), carComponentStage->GetDefaultPrim(), "GreenCar");
    success &= usdex::core::setConstantPrimvar(car1Prim.GetPrim(), sampleTokens->bodyPaintColor, Constants::green);

    if (!success)
    {
        std::cout << "Error setting body paint color primvars, exiting" << std::endl;
        return false;
    }

    // Place the cars on the track (at the start with the appropriate spacing and rotation)
    double carOffsetFromBackOfTrack = Constants::carDims[0] * 0.5 - Constants::trackDims[0] * 0.5;
    double carHeight = Constants::trackDims[1];
    double carDropHeight = Constants::carDims[0] * 0.5 * std::tan(Constants::trackAngle * M_PI / 180.0);
    double carLaneOffset = Constants::trackDims[2] * 0.25;

    transform.SetIdentity();
    transform.SetTranslation(pxr::GfVec3d(carOffsetFromBackOfTrack, -carLaneOffset, carHeight - carDropHeight));
    transform.SetRotation(pxr::GfRotation(pxr::GfVec3d(0, 1, 0), Constants::trackAngle));
    usdex::core::setLocalTransform(car0Prim, transform);

    transform.SetTranslation(pxr::GfVec3d(carOffsetFromBackOfTrack, carLaneOffset, carHeight - carDropHeight));
    transform.SetRotation(pxr::GfRotation(pxr::GfVec3d(0, 1, 0), Constants::trackAngle));
    usdex::core::setLocalTransform(car1Prim, transform);

    usdex::core::configureAssemblyHierarchy(pinewoodDerbyAssembly.GetPrim());
    return true;
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createAssembly", "Creates an assembly hierarchy using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Set the default prim to group kind to allow assembly (Model) children
    pxr::UsdModelAPI(stage->GetDefaultPrim()).SetKind(pxr::KindTokens->group);

    pxr::UsdStageRefPtr carComponentStage = createCarComponent(args);
    pxr::UsdStageRefPtr trackComponentStage = createTrackComponent(args);
    if (!carComponentStage || !trackComponentStage)
    {
        std::cout << "Error creating component stages, exiting" << std::endl;
        return -1;
    }

    std::cout << "Component stage: " << carComponentStage->GetRootLayer()->GetIdentifier() << std::endl;
    std::cout << "Component stage: " << trackComponentStage->GetRootLayer()->GetIdentifier() << std::endl;

    if (!createPinewoodDerbyAssembly(stage, trackComponentStage, carComponentStage))
    {
        std::cout << "Error creating assembly, exiting" << std::endl;
        return -1;
    }

    if (!samples::saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath))
    {
        return -1;
    }

    return 0;
}
