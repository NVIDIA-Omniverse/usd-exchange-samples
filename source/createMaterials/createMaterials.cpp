// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/MaterialAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/rtx/MaterialAlgo.h>

#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/scope.h>
#include <pxr/usd/usdGeom/sphere.h>
#include <pxr/usd/usdUtils/pipeline.h>

#include <iostream>

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

int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createMaterials", "Creates materials using the OpenUSD Exchange SDK");

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

    // Get a unique and valid material name
    pxr::TfTokenVector validMaterialNames = usdex::core::getValidChildNames(scopePrim, { "cubePbr", "sphereUvwPbr", "previewSurfacePbr" });

    // Copy textures to the stage's subdirectory
    std::string colorTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_BaseColor.png");
    std::string normalTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_N.png");
    std::string ormTex = samples::copyTextureToStagePath(args.stagePath, "Fieldstone/Fieldstone_ORM.png");


    // Create a mesh cube and bind a PBR with textures to it
    pxr::UsdGeomMesh meshPrim = samples::createCubeMesh(stage->GetDefaultPrim(), "pbrMesh", 50.0, pxr::GfVec3d(-300.0, 0.0, -300.0));
    if (!meshPrim)
    {
        std::cout << "Error creating cube mesh, exiting" << std::endl;
        return -1;
    }

    // Define a material with both MDL and USD Preview Surface shaders and material interface inputs
    pxr::UsdShadeMaterial matPrim = usdex::rtx::definePbrMaterial(
        scopePrim, /* parent prim */
        validMaterialNames[0], /* material prim name */
        pxr::GfVec3f(1, 1, 0) /* material diffuse color */
    );
    if (!matPrim)
    {
        std::cout << "Error creating mesh cube material, exiting" << std::endl;
        return -1;
    }
    usdex::rtx::addDiffuseTextureToPbrMaterial(matPrim, pxr::SdfAssetPath(colorTex));
    usdex::rtx::addOrmTextureToPbrMaterial(matPrim, pxr::SdfAssetPath(ormTex));
    usdex::rtx::addNormalTextureToPbrMaterial(matPrim, pxr::SdfAssetPath(normalTex));
    usdex::core::bindMaterial(meshPrim.GetPrim(), matPrim);


    // Create a sphere with no UVs and bind a PBR with OmniPBR that projects UVW coordinates onto the object and uses world space for projection
    // This will look correct in Omniverse RTX, but USDView will not show a textured sphere
    pxr::TfToken primName = usdex::core::getValidChildName(defaultPrim, "pbrSphere");
    pxr::SdfPath primPath = defaultPrim.GetPath().AppendChild(primName);
    pxr::UsdGeomSphere sphere = pxr::UsdGeomSphere::Define(stage, primPath);
    sphere.GetRadiusAttr().Set(50.0);
    samples::setOmniverseRefinement(sphere.GetPrim());
    samples::setExtents(sphere);
    usdex::core::setLocalTransform(
        sphere, /* xformable */
        pxr::GfVec3d(-400.0, 0.0, -400.0), /* translation */
        pxr::GfVec3d(0), /* pivot */
        pxr::GfVec3f(0), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1) /* scale */
    );

    // Define a material with both MDL and USD Preview Surface shaders and material interface inputs
    pxr::UsdShadeMaterial worldUvMatPrim = usdex::rtx::definePbrMaterial(
        scopePrim, /* parent prim */
        validMaterialNames[1], /* material prim name */
        pxr::GfVec3f(1, 1, 0) /* material diffuse color */
    );
    if (!worldUvMatPrim)
    {
        std::cout << "Error creating sphere material, exiting" << std::endl;
        return -1;
    }
    usdex::rtx::addDiffuseTextureToPbrMaterial(worldUvMatPrim, pxr::SdfAssetPath(colorTex));
    usdex::rtx::addOrmTextureToPbrMaterial(worldUvMatPrim, pxr::SdfAssetPath(ormTex));
    usdex::rtx::addNormalTextureToPbrMaterial(worldUvMatPrim, pxr::SdfAssetPath(normalTex));
    usdex::core::bindMaterial(sphere.GetPrim(), worldUvMatPrim);

    // These inputs are defined in OmniPBR.mdl, found here: `_build/target-deps/omni_core_materials/Base/OmniPBR.mdl`
    usdex::rtx::createMdlShaderInput(worldUvMatPrim, mdlInputTokens->project_uvw, pxr::VtValue(true), pxr::SdfValueTypeNames->Bool);
    usdex::rtx::createMdlShaderInput(worldUvMatPrim, mdlInputTokens->world_or_object, pxr::VtValue(true), pxr::SdfValueTypeNames->Bool);
    usdex::rtx::createMdlShaderInput(worldUvMatPrim, mdlInputTokens->texture_scale, pxr::VtValue(pxr::GfVec2f(0.01f)), pxr::SdfValueTypeNames->Float2);


    // Create a mesh cube and bind a USD Preview Surface material with textures to it
    // This material will not have an OmniPBR shader and will not use material interface inputs
    meshPrim = samples::createCubeMesh(stage->GetDefaultPrim(), "previewSurfaceMesh", 50.0, pxr::GfVec3d(-500.0, 0.0, -500.0));
    if (!meshPrim)
    {
        std::cout << "Error creating cube mesh, exiting" << std::endl;
        return -1;
    }
    matPrim = usdex::core::definePreviewMaterial(
        /* parent */ scopePrim,
        /* name */ validMaterialNames[2],
        /* color */ pxr::GfVec3f(0, 1, 0.1f)
    );
    if (!matPrim)
    {
        std::cout << "Error creating USD Preview Surface material, exiting" << std::endl;
        return -1;
    }

    usdex::core::addDiffuseTextureToPreviewMaterial(matPrim, pxr::SdfAssetPath(colorTex));
    usdex::core::addNormalTextureToPreviewMaterial(matPrim, pxr::SdfAssetPath(normalTex));
    usdex::core::addOrmTextureToPreviewMaterial(matPrim, pxr::SdfAssetPath(ormTex));
    usdex::core::bindMaterial(meshPrim.GetPrim(), matPrim);

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
