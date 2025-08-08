# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import sys

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import common.commandLine
import common.usdUtils
import usdex.core
import usdex.rtx
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    defaultPrim = stage.GetDefaultPrim()
    defaultPrimPath = defaultPrim.GetPath()
    materialScopePath = defaultPrimPath.AppendChild(UsdUtils.GetMaterialsScopeName())
    scopePrim = UsdGeom.Scope.Define(stage, materialScopePath)

    # Get unique and valid material names
    validMaterialNames = usdex.core.getValidChildNames(scopePrim.GetPrim(), ["cubePbr", "sphereUvwPbr", "previewSurfacePbr"])

    # Copy textures to the stage's subdirectory
    colorTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_BaseColor.png")
    normalTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_N.png")
    ormTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_ORM.png")

    # Create a mesh cube and bind a PBR with textures to it
    meshPrim = common.usdUtils.createCubeMesh(defaultPrim, "pbrMesh", 50.0, Gf.Vec3d(-300.0, 0.0, -300.0))
    if not meshPrim:
        print("Failure to create mesh prim")
        sys.exit(-1)

    matPrim = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=validMaterialNames[0], color=Gf.Vec3f(1, 1, 0))
    if not matPrim:
        print("Error creating mesh cube material, exiting")
        sys.exit(-1)

    usdex.rtx.addDiffuseTextureToPbrMaterial(matPrim, colorTex)
    usdex.rtx.addOrmTextureToPbrMaterial(matPrim, ormTex)
    usdex.rtx.addNormalTextureToPbrMaterial(matPrim, normalTex)
    usdex.core.bindMaterial(meshPrim.GetPrim(), matPrim)

    # Create a sphere with no UVs and bind a PBR with OmniPBR that projects UVW coordinates onto the object and uses world space for projection
    # This will look correct in Omniverse RTX, but USDView will not show a textured sphere
    primName = usdex.core.getValidChildName(defaultPrim, "pbrSphere")
    primPath = defaultPrim.GetPath().AppendChild(primName)
    sphere = UsdGeom.Sphere.Define(stage, primPath)
    sphere.GetRadiusAttr().Set(50.0)
    common.usdUtils.setOmniverseRefinement(sphere.GetPrim())
    common.usdUtils.setExtents(sphere)
    usdex.core.setLocalTransform(
        xformable=sphere,
        translation=Gf.Vec3d(-400.0, 0.0, -400.0),
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    worldUvMatPrim = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=validMaterialNames[1], color=Gf.Vec3f(1, 1, 0))
    if not matPrim:
        print("Error creating sphere material, exiting")
        sys.exit(-1)

    usdex.rtx.addDiffuseTextureToPbrMaterial(worldUvMatPrim, colorTex)
    usdex.rtx.addOrmTextureToPbrMaterial(worldUvMatPrim, ormTex)
    usdex.rtx.addNormalTextureToPbrMaterial(worldUvMatPrim, normalTex)
    usdex.core.bindMaterial(sphere.GetPrim(), worldUvMatPrim)

    # These inputs are defined in OmniPBR.mdl, found here: `_build/target-deps/omni_core_materials/Base/OmniPBR.mdl`
    usdex.rtx.createMdlShaderInput(worldUvMatPrim, "project_uvw", True, Sdf.ValueTypeNames.Bool)
    usdex.rtx.createMdlShaderInput(worldUvMatPrim, "world_or_object", True, Sdf.ValueTypeNames.Bool)
    usdex.rtx.createMdlShaderInput(worldUvMatPrim, "texture_scale", Gf.Vec2f(0.01), Sdf.ValueTypeNames.Float2)

    # Create a mesh cube and bind a USD Preview Surface material with textures to it
    # This material will not have an OmniPBR shader and will not use material interface inputs
    meshPrim = common.usdUtils.createCubeMesh(defaultPrim, "previewSurfaceMesh", 50.0, Gf.Vec3d(-500.0, 0.0, -500.0))
    if not meshPrim:
        print("Failure to create mesh prim")
        sys.exit(-1)

    matPrim = usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=validMaterialNames[2], color=Gf.Vec3f(0, 1, 0.1))
    if not matPrim:
        print("Error creating USD Preview Surface material, exiting")
        sys.exit(-1)

    usdex.core.addDiffuseTextureToPreviewMaterial(matPrim, colorTex)
    usdex.core.addNormalTextureToPreviewMaterial(matPrim, normalTex)
    usdex.core.addOrmTextureToPreviewMaterial(matPrim, ormTex)
    usdex.core.bindMaterial(meshPrim.GetPrim(), matPrim)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates materials using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
