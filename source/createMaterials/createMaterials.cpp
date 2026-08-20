// SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/MaterialAlgo.h>
#include <usdex/core/MeshAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/rtx/MaterialAlgo.h>

#include <pxr/base/gf/transform.h>
#include <pxr/base/gf/vec3f.h>
#include <pxr/base/vt/array.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/scope.h>
#include <pxr/usd/usdGeom/sphere.h>
#include <pxr/usd/usdGeom/subset.h>
#include <pxr/usd/usdUtils/pipeline.h>

#include <iostream>
#include <string>
#include <vector>

// Internal tokens
// clang-format off
PXR_NAMESPACE_USING_DIRECTIVE
TF_DEFINE_PRIVATE_TOKENS(
    mdlInputTokens,
    (project_uvw)
    (texture_scale)
    (world_or_object)
);
// clang-format on

enum Example
{
    ePreviewSurface = 0,
    eOpenPbr,
    eOmniPbr,
    ePreviewSurfaceGlass,
    eOpenPbrGlass,
    eOmniPbrGlass,
    eOmniPbrUvw,
    ePreviewSurfaceEmissive,
    eOpenPbrEmissive,
    eOmniPbrEmissive,
    ePreviewSurfaceEmissiveTexture,
    eOpenPbrEmissiveTexture,
    eOmniPbrEmissiveTexture,
    eMeshWithGeomsubsets,
    eCount
};

int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createMaterials", "Creates materials using the OpenUSD Exchange SDK");
    const bool includeOmniPbr = args.usdzPath.empty();

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();
    const pxr::SdfPath& defaultPrimPath = defaultPrim.GetPath();

    // Make path for "/Looks" scope under the default prim
    const pxr::SdfPath matScopePath = defaultPrimPath.AppendChild(pxr::UsdUtilsGetMaterialsScopeName());
    pxr::UsdPrim scopePrim = pxr::UsdGeomScope::Define(stage, matScopePath).GetPrim();
    pxr::GfTransform geometryTransform;
    geometryTransform.SetTranslation(pxr::GfVec3d(-3.75, 4.5, 0.0));
    pxr::UsdPrim geometryPrim = usdex::core::defineXform(defaultPrim, "materialSampleGrid", geometryTransform).GetPrim();

    // Keep proposed names in arrays indexed by enum so each geometry and material pair stays aligned.
    // clang-format off
    const std::vector<std::string> geomNames = {
        "previewSurfaceMesh",
        "openPbrMesh",
        "omniPbrMesh",
        "previewSurfaceGlassSphere",
        "openPbrGlassSphere",
        "omniPbrGlassSphere",
        "omniPbrUvwSphere",
        "previewSurfaceEmissiveSphere",
        "openPbrEmissiveSphere",
        "omniPbrEmissiveSphere",
        "previewSurfaceEmissiveTexture",
        "openPbrEmissiveTexture",
        "omniPbrEmissiveTexture",
        "meshWithGeomsubsets",
    };
    const std::vector<std::string> materialNames = {
        "previewSurface",
        "openPbr",
        "omniPbr",
        "previewSurfaceGlass",
        "openPbrGlass",
        "omniPbrGlass",
        "omniPbrUvw",
        "previewSurfaceEmissive",
        "openPbrEmissive",
        "omniPbrEmissive",
        "previewSurfaceEmissiveTexture",
        "openPbrEmissiveTexture",
        "omniPbrEmissiveTexture",
    };
    // clang-format on

    // Get unique and valid prim names before creating any sample geometry or materials.
    pxr::TfTokenVector validGeomNames = usdex::core::getValidChildNames(geometryPrim, geomNames);
    pxr::TfTokenVector matNames = usdex::core::getValidChildNames(scopePrim, materialNames);

    // Copy textures to the stage's subdirectory
    std::string colorTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_BaseColor.png");
    std::string normalTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_N.png");
    std::string ormTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_ORM.png");

    // Create all geometry up front. The material examples below can then focus only on authoring and binding materials.
    std::vector<pxr::UsdPrim> geometries(eCount);
    auto createMesh = [&geometryPrim, &validGeomNames](Example example, float halfHeight, const pxr::GfVec3d& position)
    {
        return samples::createCubeMesh(geometryPrim, validGeomNames[example].GetString(), halfHeight, position).GetPrim();
    };
    auto createSphere = [&geometryPrim, &validGeomNames](Example example, double radius, const pxr::GfVec3d& position)
    {
        return samples::createSphere(geometryPrim, validGeomNames[example].GetString(), radius, position).GetPrim();
    };

    const double previewX = -2.25;
    const double openPbrX = -0.75;
    const double omniPbrX = 0.75;
    const double uvwX = 2.25;
    const double emissiveY = 1.5;
    const double texturedY = 0.0;
    const double glassY = -1.5;
    const float meshHalfHeight = 0.5f;
    const double sphereRadius = 0.5;
    const float emissiveHalfHeight = 0.15f;
    const double emissiveRadius = 0.15;
    const double emissiveBottomZ = -0.15;
    const double emissiveTopZ = 0.15;
    const double meshWithGeomsubsetsZ = 0.1;

    geometries[ePreviewSurface] = createMesh(ePreviewSurface, meshHalfHeight, pxr::GfVec3d(previewX, texturedY, 0.0));
    geometries[eOpenPbr] = createMesh(eOpenPbr, meshHalfHeight, pxr::GfVec3d(openPbrX, texturedY, 0.0));
    geometries[ePreviewSurfaceGlass] = createSphere(ePreviewSurfaceGlass, sphereRadius, pxr::GfVec3d(previewX, glassY, 0.0));
    geometries[eOpenPbrGlass] = createSphere(eOpenPbrGlass, sphereRadius, pxr::GfVec3d(openPbrX, glassY, 0.0));
    geometries[ePreviewSurfaceEmissive] = createSphere(ePreviewSurfaceEmissive, emissiveRadius, pxr::GfVec3d(previewX, emissiveY, emissiveBottomZ));
    geometries[eOpenPbrEmissive] = createSphere(eOpenPbrEmissive, emissiveRadius, pxr::GfVec3d(openPbrX, emissiveY, emissiveBottomZ));
    geometries[ePreviewSurfaceEmissiveTexture] = createMesh(
        ePreviewSurfaceEmissiveTexture,
        emissiveHalfHeight,
        pxr::GfVec3d(previewX, emissiveY, emissiveTopZ)
    );
    geometries[eOpenPbrEmissiveTexture] = createMesh(eOpenPbrEmissiveTexture, emissiveHalfHeight, pxr::GfVec3d(openPbrX, emissiveY, emissiveTopZ));
    if (includeOmniPbr)
    {
        geometries[eOmniPbr] = createMesh(eOmniPbr, meshHalfHeight, pxr::GfVec3d(omniPbrX, texturedY, 0.0));
        geometries[eOmniPbrGlass] = createSphere(eOmniPbrGlass, sphereRadius, pxr::GfVec3d(omniPbrX, glassY, 0.0));
        geometries[eOmniPbrUvw] = createSphere(eOmniPbrUvw, sphereRadius, pxr::GfVec3d(uvwX, texturedY, 0.0));
        geometries[eOmniPbrEmissive] = createSphere(eOmniPbrEmissive, emissiveRadius, pxr::GfVec3d(omniPbrX, emissiveY, emissiveBottomZ));
        geometries[eOmniPbrEmissiveTexture] = createMesh(eOmniPbrEmissiveTexture, emissiveHalfHeight, pxr::GfVec3d(omniPbrX, emissiveY, emissiveTopZ));
    }

    // Mesh with GeomSubsets: next column after omniPbrGlassSphere on the glass row.
    const pxr::UsdGeomMesh meshWithGeomsubsets = samples::createMeshTabletExample(
        geometryPrim,
        validGeomNames[eMeshWithGeomsubsets].GetString(),
        pxr::GfVec3d(uvwX, glassY, meshWithGeomsubsetsZ)
    );
    geometries[eMeshWithGeomsubsets] = meshWithGeomsubsets.GetPrim();

    pxr::UsdShadeMaterial material;
    const pxr::GfVec3f white(1.0f, 1.0f, 1.0f);
    const pxr::GfVec3f glassColor(1.0f, 0.0f, 0.0f);

    // USD Preview Surface material, textures on a UV'd mesh.
    material = usdex::core::definePreviewMaterial(scopePrim, matNames[ePreviewSurface], pxr::GfVec3f(0, 1, 0.1f));
    usdex::core::addColorTextureToPreviewMaterial(material, pxr::SdfAssetPath(colorTex));
    usdex::core::addNormalTextureToPreviewMaterial(material, pxr::SdfAssetPath(normalTex));
    usdex::core::addOrmTextureToPreviewMaterial(material, pxr::SdfAssetPath(ormTex));
    usdex::core::addPreviewMaterialInterface(material);
    usdex::core::bindMaterial(geometries[ePreviewSurface], material);

    // OpenPBR material, textures on a UV'd mesh.
    material = usdex::core::definePbrMaterial(scopePrim, matNames[eOpenPbr], pxr::GfVec3f(1, 1, 0));
    usdex::core::addColorTextureToPbrMaterial(material, pxr::SdfAssetPath(colorTex));
    usdex::core::addOrmTextureToPbrMaterial(material, pxr::SdfAssetPath(ormTex));
    usdex::core::addNormalTextureToPbrMaterial(material, pxr::SdfAssetPath(normalTex));
    usdex::core::bindMaterial(geometries[eOpenPbr], material);

    if (includeOmniPbr)
    {
        // OmniPBR material, textures on a UV'd mesh.
        material = usdex::rtx::definePbrMaterial(scopePrim, matNames[eOmniPbr], pxr::GfVec3f(1, 1, 0));
        usdex::rtx::addColorTextureToPbrMaterial(material, pxr::SdfAssetPath(colorTex));
        usdex::rtx::addOrmTextureToPbrMaterial(material, pxr::SdfAssetPath(ormTex));
        usdex::rtx::addNormalTextureToPbrMaterial(material, pxr::SdfAssetPath(normalTex));
        usdex::core::bindMaterial(geometries[eOmniPbr], material);
    }

    // USD Preview Surface glass material on a sphere.
    material = usdex::core::defineGlassPreviewMaterial(scopePrim, matNames[ePreviewSurfaceGlass], glassColor);
    usdex::core::addPreviewMaterialInterface(material);
    usdex::core::bindMaterial(geometries[ePreviewSurfaceGlass], material);

    // OpenPBR glass material on a sphere.
    material = usdex::core::defineGlassPbrMaterial(scopePrim, matNames[eOpenPbrGlass], glassColor);
    usdex::core::bindMaterial(geometries[eOpenPbrGlass], material);

    if (includeOmniPbr)
    {
        // OmniPBR glass material on a sphere.
        material = usdex::rtx::defineGlassMaterial(scopePrim, matNames[eOmniPbrGlass], glassColor);
        usdex::core::bindMaterial(geometries[eOmniPbrGlass], material);

        // OmniPBR material, world-space UVW projection on a UV-less sphere.
        material = usdex::rtx::definePbrMaterial(scopePrim, matNames[eOmniPbrUvw], pxr::GfVec3f(1, 1, 0));
        usdex::rtx::addColorTextureToPbrMaterial(material, pxr::SdfAssetPath(colorTex));
        usdex::rtx::addOrmTextureToPbrMaterial(material, pxr::SdfAssetPath(ormTex));
        usdex::rtx::addNormalTextureToPbrMaterial(material, pxr::SdfAssetPath(normalTex));
        usdex::rtx::createMdlShaderInput(material, mdlInputTokens->project_uvw, pxr::VtValue(true), pxr::SdfValueTypeNames->Bool);
        usdex::rtx::createMdlShaderInput(material, mdlInputTokens->world_or_object, pxr::VtValue(true), pxr::SdfValueTypeNames->Bool);
        // The projection multiplies world-space coordinates, so this is a reciprocal of length: one texture tile per meter
        usdex::rtx::createMdlShaderInput(material, mdlInputTokens->texture_scale, pxr::VtValue(pxr::GfVec2f(1.0f)), pxr::SdfValueTypeNames->Float2);
        usdex::core::bindMaterial(geometries[eOmniPbrUvw], material);
    }

    // USD Preview Surface material, emissive color on a sphere.
    material = usdex::core::definePreviewMaterial(scopePrim, matNames[ePreviewSurfaceEmissive], white);
    usdex::core::addEmissiveColorToPreviewMaterial(material, pxr::GfVec3f(1.0f, 0.77f, 0.56f));
    usdex::core::addPreviewMaterialInterface(material);
    usdex::core::bindMaterial(geometries[ePreviewSurfaceEmissive], material);

    // OpenPBR material, emissive color on a sphere.
    material = usdex::core::definePbrMaterial(scopePrim, matNames[eOpenPbrEmissive], white);
    usdex::core::addEmissiveColorToPbrMaterial(material, pxr::GfVec3f(1.0f, 0.77f, 0.56f));
    usdex::core::bindMaterial(geometries[eOpenPbrEmissive], material);

    if (includeOmniPbr)
    {
        // OmniPBR material, emissive color on a sphere.
        material = usdex::rtx::definePbrMaterial(scopePrim, matNames[eOmniPbrEmissive], white);
        usdex::rtx::addEmissiveColorToPbrMaterial(material, pxr::GfVec3f(1.0f, 0.77f, 0.56f));
        usdex::core::bindMaterial(geometries[eOmniPbrEmissive], material);
    }

    // USD Preview Surface material, emissive texture on a UV'd mesh.
    material = usdex::core::definePreviewMaterial(scopePrim, matNames[ePreviewSurfaceEmissiveTexture], white);
    usdex::core::addEmissiveTextureToPreviewMaterial(material, pxr::SdfAssetPath(normalTex));
    usdex::core::addPreviewMaterialInterface(material);
    usdex::core::bindMaterial(geometries[ePreviewSurfaceEmissiveTexture], material);

    // OpenPBR material, emissive texture on a UV'd mesh.
    material = usdex::core::definePbrMaterial(scopePrim, matNames[eOpenPbrEmissiveTexture], white);
    usdex::core::addEmissiveTextureToPbrMaterial(material, pxr::SdfAssetPath(normalTex));
    usdex::core::bindMaterial(geometries[eOpenPbrEmissiveTexture], material);

    if (includeOmniPbr)
    {
        // OmniPBR material, emissive texture on a UV'd mesh.
        material = usdex::rtx::definePbrMaterial(scopePrim, matNames[eOmniPbrEmissiveTexture], white);
        usdex::rtx::addEmissiveTextureToPbrMaterial(material, pxr::SdfAssetPath(normalTex));
        usdex::core::bindMaterial(geometries[eOmniPbrEmissiveTexture], material);
    }

    // Bind materials to the mesh's GeomSubsets.
    // clang-format off
    static const pxr::TfTokenVector subsetNames = {
        pxr::TfToken("front"),
        pxr::TfToken("body"),
        pxr::TfToken("screen"),
    };
    static const std::vector<pxr::VtIntArray> subsetIndices = {
        pxr::VtIntArray({6, 7, 8, 9}),
        pxr::VtIntArray({0, 1, 2, 3, 4}),
        pxr::VtIntArray({5}),
    };
    // clang-format on
    const std::vector<pxr::UsdGeomSubset> geomSubsets = usdex::core::definePartitionedSubsets(meshWithGeomsubsets, subsetNames, subsetIndices);

    const pxr::TfTokenVector tabletMatNames = usdex::core::getValidChildNames(scopePrim, { "tabletFront", "tabletBody", "tabletScreen" });
    std::vector<pxr::UsdShadeMaterial> subsetMaterials = {
        usdex::core::definePreviewMaterial(scopePrim, tabletMatNames[0], pxr::GfVec3f(0.0f, 0.0f, 0.0f), 1.0f, 0.0f),
        usdex::core::definePreviewMaterial(scopePrim, tabletMatNames[1], pxr::GfVec3f(0.6f, 0.8f, 0.5f), 1.0f, 0.6f, 1.0f),
        usdex::core::definePreviewMaterial(scopePrim, tabletMatNames[2], white, 1.0f, 0.0f),
    };

    // Make the screen emissive
    usdex::core::addEmissiveColorToPreviewMaterial(subsetMaterials[2], white);
    for (auto& material : subsetMaterials)
    {
        usdex::core::addPreviewMaterialInterface(material);
    }

    usdex::core::bindMaterialSubsets(geomSubsets, subsetMaterials);

    // Save the stage to disk
    if (!samples::saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath))
    {
        return -1;
    }

    return 0;
}
