// SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//


#pragma once

#include <usdex/core/Core.h>
#include <usdex/core/Diagnostics.h>
#include <usdex/core/GprimAlgo.h>
#include <usdex/core/MeshAlgo.h>
#include <usdex/core/NameAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/vt/array.h>
#include <pxr/base/vt/types.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usd/attribute.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/boundable.h>
#include <pxr/usd/usdGeom/capsule.h>
#include <pxr/usd/usdGeom/cone.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdGeom/cylinder.h>
#include <pxr/usd/usdGeom/gprim.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/sphere.h>
#include <pxr/usd/usdGeom/tokens.h>
#include <pxr/usd/usdUtils/usdzPackage.h>

#include <filesystem>
#include <iostream>
#include <optional>
#include <string>
#include <system_error>


namespace samples
{

// Internal tokens
// clang-format off
PXR_NAMESPACE_USING_DIRECTIVE
TF_DEFINE_PRIVATE_TOKENS(
    sampleAttrTokens,
    (refinementEnableOverride)
    (refinementLevel)
);
// clang-format on

//! Get a string with authoring metadata for the samples
//! @returns A string signifying the author or a layer
std::string getSamplesAuthoringMetadata()
{
    return std::string("OpenUSD Exchange Samples");
}


//! Open or create a USD stage
//!
//! @param identifier The identifier (file path) for the stage
//! @param defaultPrimName (optional): The default prim name. Defaults to "World"
//! @param fileFormatArgs (optional): File format args if the stage doesn't already exist
//!
//! @returns The opened or created pxr::UsdStage
pxr::UsdStageRefPtr openOrCreateStage(
    const std::string& identifier,
    const std::string& defaultPrimName = std::string("World"),
    const pxr::SdfLayer::FileFormatArguments& fileFormatArgs = pxr::SdfLayer::FileFormatArguments()
)
{
    // Activate the SDK's diagnostic delegate to set the default level to "Warning" to hide "Status" messages
    usdex::core::activateDiagnosticsDelegate();
    pxr::UsdStageRefPtr stage;
    pxr::SdfLayerRefPtr layer = pxr::SdfLayer::FindOrOpen(identifier);
    if (!layer)
    {
        // NOTE: Samples use Z-up (UsdGeomTokens->z)
        stage = usdex::core::createStage(
            /* identifier */ identifier,
            /* defaultPrimName */ defaultPrimName,
            /* upAxis */ pxr::UsdGeomTokens->z,
            /* linearUnits */ pxr::UsdGeomLinearUnits::meters,
            /* authoringMetadata */ getSamplesAuthoringMetadata(),
            /* file format args */ fileFormatArgs
        );
    }
    else
    {
        stage = pxr::UsdStage::Open(layer);
    }
    return stage;
}

//! Package a saved stage and its dependencies into a USDZ archive
//!
//! @param stage The stage whose root layer should be packaged
//! @param usdzPath Destination path for the USDZ package
//!
//! @returns true if the USDZ package was created
bool packageStageAsUsdz(const pxr::UsdStageRefPtr& stage, const std::string& usdzPath)
{
    if (!stage)
    {
        std::cout << "Error packaging USDZ: invalid stage" << std::endl;
        return false;
    }

    std::string rootLayerPath = stage->GetRootLayer()->GetRealPath();
    if (rootLayerPath.empty())
    {
        rootLayerPath = stage->GetRootLayer()->GetIdentifier();
    }
    if (rootLayerPath.empty())
    {
        std::cout << "Error packaging USDZ: stage root layer has no file path" << std::endl;
        return false;
    }

    const std::filesystem::path absRootLayerPath = std::filesystem::absolute(rootLayerPath);
    const std::filesystem::path absUsdzPath = std::filesystem::absolute(usdzPath);
    const pxr::SdfAssetPath asset(absRootLayerPath.string());
    if (!pxr::UsdUtilsCreateNewUsdzPackage(asset, absUsdzPath.string()))
    {
        std::error_code error;
        std::filesystem::remove(absUsdzPath, error);
        std::cout << "Error creating USDZ package: " << usdzPath << std::endl;
        return false;
    }

    std::cout << "Created USDZ package: " << usdzPath << std::endl;
    return true;
}

//! Save a stage and optionally package it as USDZ
//!
//! @param stage The stage to save
//! @param authoringMetadata The metadata written to authored layers
//! @param usdzPath Optional USDZ package destination. If empty, no package is created.
//!
//! @returns true if the stage saved and optional USDZ package was created
bool saveStage(const pxr::UsdStageRefPtr& stage, const std::string& authoringMetadata, const std::string& usdzPath = std::string())
{
    usdex::core::saveStage(stage, authoringMetadata);
    if (!usdzPath.empty())
    {
        return packageStageAsUsdz(stage, usdzPath);
    }
    return true;
}


// Set custom attributes for curved geom prim refinement in NVIDIA Omniverse RTX
void setOmniverseRefinement(pxr::UsdPrim prim, bool enabled = true, int level = 2)
{
    pxr::UsdAttribute attr = prim.CreateAttribute(sampleAttrTokens->refinementEnableOverride, pxr::SdfValueTypeNames->Bool, /* custom */ true);
    attr.Set(enabled);
    attr.SetDisplayName("omniRefinementEnableOverride");
    attr = prim.CreateAttribute(sampleAttrTokens->refinementLevel, pxr::SdfValueTypeNames->Int, /* custom */ true);
    attr.Set(level);
    attr.SetDisplayName("omniRefinementLevel");
}


// Compute and set the extents on a prim
void setExtents(pxr::UsdGeomBoundable prim)
{
    pxr::VtArray<pxr::GfVec3f> extent;
    pxr::UsdGeomBoundable::ComputeExtentFromPlugins(prim, pxr::UsdTimeCode::Default(), &extent);
    prim.GetExtentAttr().Set(extent);
}


//! Set the transform of a prim
//!
//! @param prim The prim to set the transform
//! @param position Position of the prim
//! @param rotation Rotation of the prim
//! @param scale Scale of the prim
void setTransform(
    pxr::UsdPrim prim,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt
)
{
    if (position.has_value() || rotation.has_value() || scale.has_value())
    {
        const pxr::GfVec3d pivotValue(0);
        const pxr::GfVec3d positionValue = position.has_value() ? position.value() : pxr::GfVec3d(0);
        const pxr::GfVec3f rotationValue = rotation.has_value() ? rotation.value() : pxr::GfVec3f(0);
        const pxr::GfVec3f scaleValue = scale.has_value() ? scale.value() : pxr::GfVec3f(1);
        usdex::core::setLocalTransform(prim, positionValue, pivotValue, rotationValue, usdex::core::RotationOrder::eXyz, scaleValue);
    }
}


//! Create a UsdGeom::Cone as a child of the parent prim with Omniverse refinement and extents
//!
//! @param parent The parent prim to create the cone under
//! @param name The proposed name of the cone prim. Defaults to "cone"
//! @param axis The axis of the cone. Defaults to UsdGeomTokens->z
//! @param height The height of the cone. Defaults to 1
//! @param radius The radius of the cone. Defaults to 0.5
//! @param position Position of the cone
//! @param rotation Rotation of the cone
//! @param scale Scale of the cone
//! @param displayColor Display color of the cone
//! @return The created pxr::UsdGeomCone
pxr::UsdGeomCone createCone(
    pxr::UsdPrim parent,
    const std::string& name = "cone",
    pxr::TfToken axis = pxr::UsdGeomTokens->z,
    double height = 1.0,
    double radius = 0.5,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt,
    std::optional<pxr::GfVec3f> displayColor = std::nullopt
)
{
    // Get a valid, unique child prim name under the parent prim
    const pxr::TfToken validToken = usdex::core::getValidChildName(parent, name);
    pxr::UsdGeomCone cone = usdex::core::defineCone(parent, validToken.GetString(), radius, height, axis, displayColor);
    setOmniverseRefinement(cone.GetPrim());

    // Set transform.
    setTransform(cone.GetPrim(), position, rotation, scale);

    return cone;
}


//! Create a sphere prim as a child of the parent prim
//!
//! @param parent The parent prim to create the sphere under
//! @param name The proposed name of the sphere prim. Defaults to "sphere"
//! @param radius The radius of the sphere. Defaults to 0.5
//! @param position Position of the sphere
//! @param rotation Rotation of the sphere
//! @param scale Scale of the sphere
//! @param displayColor Display color of the sphere
//! @return The created pxr::UsdGeomSphere
pxr::UsdGeomSphere createSphere(
    pxr::UsdPrim parent,
    const std::string& name = "sphere",
    double radius = 0.5,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt,
    std::optional<pxr::GfVec3f> displayColor = std::nullopt
)
{
    // Get a valid, unique child prim name under the parent prim
    const pxr::TfToken validToken = usdex::core::getValidChildName(parent, name);
    pxr::UsdGeomSphere sphere = usdex::core::defineSphere(parent, validToken.GetString(), radius, displayColor);
    setOmniverseRefinement(sphere.GetPrim());

    // Set transform.
    setTransform(sphere.GetPrim(), position, rotation, scale);

    return sphere;
}


//! Create a cube prim as a child of the parent prim
//!
//! @param parent The parent prim to create the cube under
//! @param name The proposed name of the cube prim
//! @param size The size of the cube. Defaults to 1
//! @param position Position of the cube
//! @param rotation Rotation of the cube
//! @param scale Scale of the cube
//! @param displayColor Display color of the cube
//! @return The created pxr::UsdGeomCube
pxr::UsdGeomCube createCube(
    pxr::UsdPrim parent,
    const std::string& name = "cube",
    double size = 1.0,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt,
    std::optional<pxr::GfVec3f> displayColor = std::nullopt
)
{
    // Get a valid, unique child prim name under the parent prim
    const pxr::TfToken validToken = usdex::core::getValidChildName(parent, name);
    pxr::UsdGeomCube cube = usdex::core::defineCube(parent, validToken.GetString(), size, displayColor);

    // Set transform.
    setTransform(cube.GetPrim(), position, rotation, scale);

    return cube;
}


//! Create a UsdGeom::Cylinder as a child of the parent prim with Omniverse refinement and extents
//!
//! @param parent The parent prim to create the cylinder under
//! @param name The proposed name of the cylinder prim. Defaults to "cylinder"
//! @param axis The axis of the cylinder. Defaults to UsdGeomTokens->z
//! @param height The height of the cylinder. Defaults to 4
//! @param radius The radius of the cylinder. Defaults to 0.5
//! @param position Position of the cylinder
//! @param rotation Rotation of the cylinder
//! @param scale Scale of the cylinder
//! @param displayColor Display color of the cylinder
//! @return The created pxr::UsdGeomCylinder
pxr::UsdGeomCylinder createCylinder(
    pxr::UsdPrim parent,
    const std::string& name = "cylinder",
    pxr::TfToken axis = pxr::UsdGeomTokens->z,
    double height = 4.0,
    double radius = 0.5,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt,
    std::optional<pxr::GfVec3f> displayColor = std::nullopt
)
{
    // Get a valid, unique child prim name under the parent prim
    const pxr::TfToken validToken = usdex::core::getValidChildName(parent, name);
    pxr::UsdGeomCylinder cylinder = usdex::core::defineCylinder(parent, validToken.GetString(), radius, height, axis, displayColor);
    setOmniverseRefinement(cylinder.GetPrim());

    // Set transform.
    setTransform(cylinder.GetPrim(), position, rotation, scale);

    return cylinder;
}


//! Create a UsdGeom::Capsule as a child of the parent prim with Omniverse refinement and extents
//!
//! @param parent The parent prim to create the capsule under
//! @param name The proposed name of the capsule prim. Defaults to "capsule"
//! @param axis The axis of the capsule. Defaults to UsdGeomTokens->z
//! @param height The height of the capsule. Defaults to 1
//! @param radius The radius of the capsule. Defaults to 0.5
//! @param position Position of the capsule
//! @param rotation Rotation of the capsule
//! @param scale Scale of the capsule
//! @param displayColor Display color of the capsule
//! @return The created pxr::UsdGeomCapsule
pxr::UsdGeomCapsule createCapsule(
    pxr::UsdPrim parent,
    const std::string& name = "capsule",
    pxr::TfToken axis = pxr::UsdGeomTokens->z,
    double height = 1.0,
    double radius = 0.5,
    std::optional<pxr::GfVec3d> position = std::nullopt,
    std::optional<pxr::GfVec3f> rotation = std::nullopt,
    std::optional<pxr::GfVec3f> scale = std::nullopt,
    std::optional<pxr::GfVec3f> displayColor = std::nullopt
)
{
    const pxr::TfToken validToken = usdex::core::getValidChildName(parent, name);
    pxr::UsdGeomCapsule capsule = usdex::core::defineCapsule(parent, validToken.GetString(), radius, height, axis, displayColor);
    setOmniverseRefinement(capsule.GetPrim());

    // Set transform.
    setTransform(capsule.GetPrim(), position, rotation, scale);

    return capsule;
}


//! Creates a cube mesh with the specified half height and local position
//!
//! @brief The cube mesh prim will be a child of the parent parameter
//!
//! @param parent The parent prim for the new cube mesh
//! @param meshName The name of the mesh. Defaults to "cubeMesh"
//! @param halfHeight The half height of the cube. Defaults to 0.5
//! @param localPos The local position of the cube. Defaults to 0,0,0
//! @return The created pxr::UsdGeomMesh
pxr::UsdGeomMesh createCubeMesh(
    pxr::UsdPrim parent,
    const std::string& meshName = "cubeMesh",
    float halfHeight = 0.5f,
    const pxr::GfVec3d& localPos = pxr::GfVec3d(0.0)
)
{
    // clang-format off
    const float h = halfHeight;
    static const pxr::VtArray<int> faceVertexIndices = {
        0, 1, 2, 1, 3, 2,
        4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11,
        12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19,
        20, 21, 22, 20, 22, 23
    };
    static const pxr::VtArray<pxr::GfVec3f> normals = {
        {0, 1, 0}, {0, 1, 0}, {0, 1, 0}, {0, 1, 0},
        {0, -1, 0}, {0, -1, 0}, {0, -1, 0}, {0, -1, 0},
        {0, 0, -1}, {0, 0, -1}, {0, 0, -1}, {0, 0, -1},
        {1, 0, 0}, {1, 0, 0}, {1, 0, 0}, {1, 0, 0},
        {0, 0, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1},
        {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}
    };
    const pxr::VtArray<pxr::GfVec3f> points = {
        {h, h, -h}, {-h, h, -h}, {h, h, h}, {-h, h, h},
        {h, -h, h}, {-h, -h, h}, {-h, -h, -h}, {h, -h, -h},
        {h, -h, -h}, {-h, -h, -h}, {-h, h, -h}, {h, h, -h},
        {h, -h, h}, {h, -h, -h}, {h, h, -h}, {h, h, h},
        {-h, -h, h}, {h, -h, h}, {h, h, h}, {-h, h, h},
        {-h, -h, -h}, {-h, -h, h}, {-h, h, h}, {-h, h, -h}
    };
    static const pxr::VtArray<pxr::GfVec2f> uvs = {
        {0, 0}, {0, 1}, {1, 1}, {1, 0},
        {0, 0}, {0, 1}, {1, 1}, {1, 0},
        {0, 0}, {0, 1}, {1, 1}, {1, 0},
        {0, 0}, {0, 1}, {1, 1}, {1, 0},
        {0, 0}, {0, 1}, {1, 1}, {1, 0},
        {0, 0}, {0, 1}, {1, 1}, {1, 0}
    };
    // clang-format on

    pxr::TfTokenVector meshPrimNames = usdex::core::getValidChildNames(parent, std::vector<std::string>{ meshName });
    if (meshName != meshPrimNames[0])
    {
        std::cout << "Renaming input mesh name <" << meshName << "> to the valid USD prim name <" << meshPrimNames[0] << ">" << std::endl;
    }
    const pxr::SdfPath meshPrimPath = parent.GetPath().AppendChild(meshPrimNames[0]);

    // Face vertex count - 2 Triangles per face * 6 faces
    static const pxr::VtArray<int> faceVertexCounts = { 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3 };

    // Index the normals and UVs
    auto normalPrimvarData = usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->vertex, normals);
    normalPrimvarData.index();

    auto uvPrimvarData = usdex::core::Vec2fPrimvarData(pxr::UsdGeomTokens->vertex, uvs);
    uvPrimvarData.index();

    // Create the geometry under the default prim
    pxr::UsdGeomMesh mesh = usdex::core::definePolyMesh(
        parent.GetStage(), /* parent prim */
        meshPrimPath, /* name */
        faceVertexCounts,
        faceVertexIndices,
        points,
        normalPrimvarData, /* normals */
        uvPrimvarData, /* uvs */
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, { { 0.463f, 0.725f, 0.0f } }) /* displayColor */
    );
    if (!mesh)
    {
        return mesh;
    }

    // Set the display name if the input name was not "valid", the display name can handle UTF-8 characters
    if (meshName != meshPrimNames[0])
    {
        usdex::core::setDisplayName(mesh.GetPrim(), meshName);
    }

    // Set transform information if not at origin
    if (localPos != pxr::GfVec3d(0.0))
    {
        usdex::core::setLocalTransform(
            mesh, /* xformable */
            localPos, /* translation */
            pxr::GfVec3d(0.0), /* pivot */
            pxr::GfVec3f(0.0), /* rotation */
            usdex::core::RotationOrder::eXyz,
            pxr::GfVec3f(1.0) /* scale */
        );
    }

    return mesh;
}


//! Creates a tablet-like mesh used by the createMaterials GeomSubset example
//!
//! @brief The mesh prim will be a child of the parent parameter. Face partitions
//! for material binding are authored separately with `definePartitionedSubsets`.
//!
//! @param parent The parent prim for the new mesh
//! @param meshName The name of the mesh. Defaults to "meshWithGeomsubsets"
//! @param localPos The local position of the mesh. Defaults to 0,0,0
//! @return The created pxr::UsdGeomMesh
pxr::UsdGeomMesh createMeshTabletExample(
    pxr::UsdPrim parent,
    const std::string& meshName = "meshWithGeomsubsets",
    const pxr::GfVec3d& localPos = pxr::GfVec3d(0.0)
)
{
    // clang-format off
    static const pxr::VtArray<int> faceVertexCounts(10, 4);
    static const pxr::VtArray<int> faceVertexIndices = {
        0, 1, 3, 2, 2, 3, 7, 6, 6, 7, 5, 4, 4, 5, 1, 0,
        2, 6, 4, 0, 8, 9, 10, 11, 9, 8, 7, 3, 10, 9, 3, 1,
        11, 10, 1, 5, 8, 11, 5, 7,
    };
    // Uniform normals: one normal per face (collapsed from faceVarying source data).
    static const pxr::VtArray<pxr::GfVec3f> normals = {
        {-1, 0, 0}, {0, 0, 1}, {1, 0, 0}, {0, 0, -1}, {0, 1, 0},
        {0, -1, 0}, {0, -1, 0}, {0, -1, 0}, {0, -1, 0}, {0, -1, 0},
    };
    static const pxr::VtArray<pxr::GfVec3f> points = {
        {-0.25f, 0.0525f, -0.4f}, {-0.25f, 0.0025f, -0.4f}, {-0.25f, 0.0525f, 0.4f}, {-0.25f, 0.0025f, 0.4f},
        {0.25f, 0.0525f, -0.4f}, {0.25f, 0.0025f, -0.4f}, {0.25f, 0.0525f, 0.4f}, {0.25f, 0.0025f, 0.4f},
        {0.2f, 0.0025f, 0.3f}, {-0.2f, 0.0025f, 0.3f}, {-0.2f, 0.0025f, -0.3f}, {0.2f, 0.0025f, -0.3f},
    };
    static const pxr::VtArray<pxr::GfVec2f> uvs = {
        {0.913f, 0.696f}, {1.0f, 0.435f}, {0.435f, 0.0f}, {0.87f, 0.696f},
        {0.957f, 0.435f}, {0.913f, 0.0f}, {1.0f, 0.435f}, {0.435f, 0.696f},
        {0.87f, 0.0f}, {0.957f, 0.435f}, {0.957f, 0.0f}, {1.0f, 0.87f},
        {0.0f, 0.0f}, {0.913f, 0.0f}, {0.957f, 0.87f}, {1.0f, 0.0f},
        {0.957f, 0.696f}, {0.0f, 0.696f}, {0.957f, 0.0f}, {0.913f, 0.696f},
        {0.826f, 0.609f}, {0.478f, 0.609f}, {0.478f, 0.087f}, {0.826f, 0.087f},
        {0.435f, 0.696f}, {0.87f, 0.696f}, {0.435f, 0.0f}, {0.87f, 0.0f},
    };
    static const pxr::VtArray<int> uvIndices = {
        0, 3, 8, 5, 6, 9, 18, 15, 16, 19, 13, 10, 11, 14, 4, 1,
        7, 17, 12, 2, 20, 21, 22, 23, 21, 20, 25, 24, 22, 21, 24, 26,
        23, 22, 26, 27, 20, 23, 27, 25,
    };
    // clang-format on

    const pxr::TfToken meshPrimName = usdex::core::getValidChildName(parent, meshName);
    if (meshPrimName != meshName)
    {
        std::cout << "Renaming input mesh name <" << meshName << "> to the valid USD prim name <" << meshPrimName << ">" << std::endl;
    }

    auto normalsPrimvarData = usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->uniform, normals);
    normalsPrimvarData.index();
    auto uvsPrimvarData = usdex::core::Vec2fPrimvarData(pxr::UsdGeomTokens->faceVarying, uvs, uvIndices);
    uvsPrimvarData.index();

    pxr::UsdGeomMesh mesh = usdex::core::definePolyMesh(
        parent,
        meshPrimName.GetString(),
        faceVertexCounts,
        faceVertexIndices,
        points,
        normalsPrimvarData,
        uvsPrimvarData,
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, { { 0.5f, 0.5f, 0.5f } })
    );
    if (!mesh)
    {
        return mesh;
    }

    usdex::core::setEffectiveDisplayName(mesh.GetPrim(), meshName);

    if (localPos != pxr::GfVec3d(0.0))
    {
        usdex::core::setLocalTransform(mesh, localPos, pxr::GfVec3d(0.0), pxr::GfVec3f(0.0), usdex::core::RotationOrder::eXyz, pxr::GfVec3f(1.0));
    }

    return mesh;
}


//! Creates a wedge mesh (triangular prism) with the specified dimensions and local position
//!
//! @brief The wedge mesh prim will be a child of the parent parameter
//!
//! @param parent The parent prim for the new wedge mesh
//! @param meshName The name of the mesh. Defaults to "wedgeMesh"
//! @param height The height scale of the wedge. Defaults to 1.0
//! @param length The length scale of the wedge. Defaults to 1.0
//! @param width The width scale of the wedge. Defaults to 1.0
//! @param localPos The local position of the wedge. Defaults to 0,0,0
//! @return The created pxr::UsdGeomMesh
pxr::UsdGeomMesh createWedge(
    pxr::UsdPrim parent,
    const std::string& meshName = "wedgeMesh",
    float height = 1.0f,
    float length = 1.0f,
    float width = 1.0f,
    const pxr::GfVec3d& localPos = pxr::GfVec3d(0.0)
)
{
    const float h = 0.5f;

    // Wedge points (6 vertices total)
    // clang-format off
    static const pxr::VtArray<pxr::GfVec3f> points = {
        { h, -h, -h }, // Vertex 0: (1, -1, -1) scaled
        { h, h, -h }, // Vertex 1: (1, 1, -1) scaled
        { -h, -h, h }, // Vertex 2: (-1, -1, 1) scaled
        { -h, h, h }, // Vertex 3: (-1, 1, 1) scaled
        { -h, -h, -h }, // Vertex 4: (-1, -1, -1) scaled
        { -h, h, -h }, // Vertex 5: (-1, 1, -1) scaled
    };
    // Wedge vertex indices and counts
    // 5 faces: 3 triangular (3 vertices each), 2 rectangular (4 vertices each)
    static const pxr::VtArray<int> faceVertexIndices = {
        0, 2, 4,
        1, 0, 4, 5,
        5, 4, 2, 3,
        3, 1, 5,
        3, 2, 0, 1
    };
    static const pxr::VtArray<int> faceVertexCounts = { 3, 4, 4, 3, 4 };

    // Normals for each face vertex (18 normals total)
    static const pxr::VtArray<pxr::GfVec3f> normals = {
        { 0, -1, 0 }, { 0, -1, 0 }, { 0, -1, 0 }, // Face 1 (3 vertices)
        { 0, 0, -1 }, { 0, 0, -1 }, { 0, 0, -1 }, { 0, 0, -1 }, // Face 2 (4 vertices)
        { -1, 0, 0 }, { -1, 0, 0 }, { -1, 0, 0 }, { -1, 0, 0 }, // Face 3 (4 vertices)
        { 0, 1, 0 }, { 0, 1, 0 }, { 0, 1, 0 }, // Face 4 (3 vertices)
        { 0.70710677f, 0, 0.70710677f }, { 0.70710677f, 0, 0.70710677f }, { 0.70710677f, 0, 0.70710677f }, { 0.70710677f, 0, 0.70710677f } // Face 5
    };
    // clang-format on

    pxr::TfTokenVector meshPrimNames = usdex::core::getValidChildNames(parent, std::vector<std::string>{ meshName });
    if (meshName != meshPrimNames[0])
    {
        std::cout << "Renaming input mesh name <" << meshName << "> to the valid USD prim name <" << meshPrimNames[0] << ">" << std::endl;
    }
    const pxr::SdfPath meshPrimPath = parent.GetPath().AppendChild(meshPrimNames[0]);

    // Index the normals
    auto normalPrimvarData = usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->faceVarying, normals);
    normalPrimvarData.index();

    // Create the geometry under the parent prim
    pxr::UsdGeomMesh mesh = usdex::core::definePolyMesh(
        parent.GetStage(), /* parent prim */
        meshPrimPath, /* name */
        faceVertexCounts,
        faceVertexIndices,
        points,
        normalPrimvarData, /* normals */
        std::nullopt, /* uvs */
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, { { 1.0f, 0.0f, 0.0f } }) /* displayColor */
    );
    if (!mesh)
    {
        return mesh;
    }

    // Set the display name if the input name was not "valid", the display name can handle UTF-8 characters
    if (meshName != meshPrimNames[0])
    {
        usdex::core::setDisplayName(mesh.GetPrim(), meshName);
    }

    // Set transform information with scaling and position
    usdex::core::setLocalTransform(
        mesh, /* xformable */
        localPos, /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(0.0), /* rotation */
        usdex::core::RotationOrder::eXyz,
        pxr::GfVec3f(length, width, height) /* scale */
    );

    return mesh;
}

} // namespace samples
