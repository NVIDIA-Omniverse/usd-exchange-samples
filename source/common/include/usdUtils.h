// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//


#pragma once

#include <usdex/core/Core.h>
#include <usdex/core/MeshAlgo.h>
#include <usdex/core/NameAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usd/attribute.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/boundable.h>
#include <pxr/usd/usdGeom/cone.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdGeom/cylinder.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/tokens.h>

#include <iostream>
#include <string>


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
    pxr::UsdStageRefPtr stage;
    pxr::SdfLayerRefPtr layer = pxr::SdfLayer::FindOrOpen(identifier);
    if (!layer)
    {
        stage = usdex::core::createStage(
            /* identifier */ identifier,
            /* defaultPrimName */ defaultPrimName,
            /* upAxis */ pxr::UsdGeomGetFallbackUpAxis(),
            /* linearUnits */ pxr::UsdGeomLinearUnits::centimeters,
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


// Set custom attributes for curved geom prim refinement in NVIDIA Omniverse RTX
void setOmniverseRefinement(pxr::UsdPrim prim, bool enabled = true, int level = 2)
{
    pxr::UsdAttribute attr = prim.CreateAttribute(sampleAttrTokens->refinementEnableOverride, pxr::SdfValueTypeNames->Bool);
    attr.Set(enabled);
    attr.SetDisplayName("omniRefinementEnableOverride");
    attr = prim.CreateAttribute(sampleAttrTokens->refinementLevel, pxr::SdfValueTypeNames->Int);
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


//! Create a UsdGeom::Cone as a child of the parent prim with Omniverse refinement and extents
//!
//! @param parent The parent prim to create the cone under
//! @param name The proposed name of the cone prim. Defaults to "cone"
//! @param axis The axis of the cone. Defaults to UsdGeomGetFallbackUpAxis(), which is typically UsdGeomTokens->y
//! @param height The height of the cone. Defaults to 100
//! @param radius The radius of the cone. Defaults to 50
//! @return The created pxr::UsdGeomCone
pxr::UsdGeomCone createCone(
    pxr::UsdPrim parent,
    const std::string& name = "cone",
    pxr::TfToken axis = pxr::UsdGeomGetFallbackUpAxis(),
    double height = 100.0,
    double radius = 50.0
)
{
    // Get a valid, unique child prim name under the parent prim
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(parent, std::vector<std::string>{ name });
    const pxr::SdfPath primPath = parent.GetPath().AppendChild(validTokens[0]);
    pxr::UsdGeomCone cone = pxr::UsdGeomCone::Define(parent.GetStage(), primPath);
    cone.GetAxisAttr().Set(axis);
    cone.GetHeightAttr().Set(height);
    cone.GetRadiusAttr().Set(radius);
    setOmniverseRefinement(cone.GetPrim());
    setExtents(cone);
    return cone;
}


//! Create a cube prim as a child of the parent prim
//!
//! @param parent The parent prim to create the cube under
//! @param name The proposed name of the cube prim
//! @param size The size of the cube. Defaults to 100
//! @return The created pxr::UsdGeomCube
pxr::UsdGeomCube createCube(pxr::UsdPrim parent, const std::string& name = "cube", double size = 100.0)
{
    // Get a valid, unique child prim name under the parent prim
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(parent, std::vector<std::string>{ name });
    const pxr::SdfPath cubePrimPath = parent.GetPath().AppendChild(validTokens[0]);
    pxr::UsdGeomCube cube = pxr::UsdGeomCube::Define(parent.GetStage(), cubePrimPath);
    cube.GetSizeAttr().Set(size);
    setExtents(cube);
    return cube;
}


//! Create a UsdGeom::Cylinder as a child of the parent prim with Omniverse refinement and extents
//!
//! @param parent The parent prim to create the cylinder under
//! @param name The proposed name of the cylinder prim. Defaults to "cylinder"
//! @param axis The axis of the cylinder. Defaults to UsdGeomGetFallbackUpAxis(), which is typically UsdGeomTokens->y
//! @param height The height of the cylinder. Defaults to 400
//! @param radius The radius of the cylinder. Defaults to 50
//! @return The created pxr::UsdGeomCylinder
pxr::UsdGeomCylinder createCylinder(
    pxr::UsdPrim parent,
    const std::string& name = "cylinder",
    pxr::TfToken axis = pxr::UsdGeomGetFallbackUpAxis(),
    double height = 400.0,
    double radius = 50.0
)
{
    // Get a valid, unique child prim name under the parent prim
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(parent, std::vector<std::string>{ name });
    const pxr::SdfPath primPath = parent.GetPath().AppendChild(validTokens[0]);
    pxr::UsdGeomCylinder cylinder = pxr::UsdGeomCylinder::Define(parent.GetStage(), primPath);
    cylinder.GetAxisAttr().Set(axis);
    cylinder.GetHeightAttr().Set(height);
    cylinder.GetRadiusAttr().Set(radius);
    setOmniverseRefinement(cylinder.GetPrim());
    setExtents(cylinder);
    return cylinder;
}


//! Creates a cube mesh with the specified half height and local position
//!
//! @brief The cube mesh prim will be a child of the parent parameter
//!
//! @param parent The parent prim for the new cube mesh
//! @param meshName The name of the mesh. Defaults to "cubeMesh"
//! @param halfHeight The half height of the cube. Defaults to 50.0
//! @param localPos The local position of the cube. Defaults to 0,0,0
//! @return The created pxr::UsdGeomMesh
pxr::UsdGeomMesh createCubeMesh(
    pxr::UsdPrim parent,
    const std::string& meshName = "cubeMesh",
    float halfHeight = 50.0f,
    const pxr::GfVec3d& localPos = pxr::GfVec3d(0.0)
)
{
    // clang-format off
    const float h = halfHeight;
    int cubeVertexIndices[] = {
        0, 1, 2, 1, 3, 2,
        4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11,
        12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19,
        20, 21, 22, 20, 22, 23
    };
    float cubeNormals[][3] = {
        {0, 0, -1}, {0, 0, -1}, {0, 0, -1}, {0, 0, -1},
        {0, 0, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1},
        {0, -1, 0}, {0, -1, 0}, {0, -1, 0}, {0, -1, 0},
        {1, 0, 0}, {1, 0, 0}, {1, 0, 0}, {1, 0, 0},
        {0, 1, 0}, {0, 1, 0}, {0, 1, 0}, {0, 1, 0},
        {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}, {-1, 0, 0}
    };
    float cubePoints[][3] = {
        {h, -h, -h}, {-h, -h, -h}, {h, h, -h}, {-h, h, -h},
        {h, h, h}, {-h, h, h}, {-h, -h, h}, {h, -h, h},
        {h, -h, h}, {-h, -h, h}, {-h, -h, -h}, {h, -h, -h},
        {h, h, h}, {h, -h, h}, {h, -h, -h}, {h, h, -h},
        {-h, h, h}, {h, h, h}, {h, h, -h}, {-h, h, -h},
        {-h, -h, h}, {-h, h, h}, {-h, h, -h}, {-h, -h, -h}
    };
    float cubeUV[][2] = {
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

    // Face vertex count
    pxr::VtArray<int> faceVertexCounts;
    faceVertexCounts.resize(12); // 2 Triangles per face * 6 faces
    std::fill(faceVertexCounts.begin(), faceVertexCounts.end(), 3); // Triangle

    // Calculate indices for each triangle
    size_t num_indices = std::size(cubeVertexIndices); // 2 Triangles per face * 3 Vertices per Triangle * 6 Faces
    pxr::VtArray<int> faceVertexIndices;
    faceVertexIndices.resize(num_indices);
    for (size_t i = 0; i < num_indices; i++)
    {
        faceVertexIndices[i] = cubeVertexIndices[i];
    }

    // all of the vertices
    size_t num_vertices = std::size(cubePoints);
    pxr::VtArray<pxr::GfVec3f> points;
    points.resize(num_vertices);
    for (size_t i = 0; i < num_vertices; i++)
    {
        points[i] = pxr::GfVec3f(cubePoints[i][0], cubePoints[i][1], cubePoints[i][2]);
    }

    // normals
    size_t num_normals = std::size(cubeNormals);
    pxr::VtArray<pxr::GfVec3f> normals;
    normals.resize(num_normals);
    for (size_t i = 0; i < num_normals; i++)
    {
        normals[i] = pxr::GfVec3f((float)cubeNormals[i][0], (float)cubeNormals[i][1], (float)cubeNormals[i][2]);
    }
    auto normalPrimvarData = usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->vertex, normals);
    normalPrimvarData.index();

    // UV (st)
    size_t uv_count = std::size(cubeUV);
    pxr::VtVec2fArray uvs;
    uvs.resize(uv_count);
    for (size_t i = 0; i < uv_count; ++i)
    {
        uvs[i].Set(cubeUV[i]);
    }
    auto uvPrimvarData = usdex::core::Vec2fPrimvarData(pxr::UsdGeomTokens->vertex, uvs);
    uvPrimvarData.index();

    // Create the geometry under the default prim
    pxr::UsdGeomMesh mesh = usdex::core::definePolyMesh(
        parent.GetStage(), /* parent prim */
        meshPrimPath, /* name */
        faceVertexCounts, /* faceVertexCounts */
        faceVertexIndices, /* faceVertexIndices */
        points, /* points */
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
            mesh.GetPrim(), /* parent prim */
            localPos, /* translation */
            pxr::GfVec3d(0.0), /* pivot */
            pxr::GfVec3f(0.0), /* rotation */
            usdex::core::RotationOrder::eXyz,
            pxr::GfVec3f(1.0) /* scale */
        );
    }

    return mesh;
}

} // namespace samples
