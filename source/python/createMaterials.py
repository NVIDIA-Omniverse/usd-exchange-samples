# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys
from enum import IntEnum

import common.commandLine
import common.usdUtils
import usdex.core
import usdex.rtx
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils, Vt


class Example(IntEnum):
    PREVIEW_SURFACE = 0
    OPENPBR = 1
    OMNIPBR = 2
    PREVIEW_SURFACE_GLASS = 3
    OPENPBR_GLASS = 4
    OMNIPBR_GLASS = 5
    OMNIPBR_UVW = 6
    PREVIEW_SURFACE_EMISSIVE = 7
    OPENPBR_EMISSIVE = 8
    OMNIPBR_EMISSIVE = 9
    PREVIEW_SURFACE_EMISSIVE_TEXTURE = 10
    OPENPBR_EMISSIVE_TEXTURE = 11
    OMNIPBR_EMISSIVE_TEXTURE = 12
    MESH_WITH_GEOMSUBSETS = 13


def main(args):
    print(f"Stage path: {args.path}")
    includeOmniPbr = args.usdzPath is None

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    defaultPrim = stage.GetDefaultPrim()
    defaultPrimPath = defaultPrim.GetPath()
    materialScopePath = defaultPrimPath.AppendChild(UsdUtils.GetMaterialsScopeName())
    scopePrim = UsdGeom.Scope.Define(stage, materialScopePath)
    geometryOrigin = Gf.Vec3d(-3.75, 4.5, 0.0)
    geometryPrim = usdex.core.defineXform(defaultPrim, "materialSampleGrid", Gf.Transform(geometryOrigin)).GetPrim()
    E = Example

    # Keep proposed names in arrays indexed by enum so each geometry and material pair stays aligned.
    geomNames = [
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
    ]
    materialNames = [
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
    ]

    # Get unique and valid prim names before creating any sample geometry or materials.
    validGeomNames = usdex.core.getValidChildNames(geometryPrim, geomNames)
    matNames = usdex.core.getValidChildNames(scopePrim.GetPrim(), materialNames)

    # Copy textures to the stage's subdirectory
    colorTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_BaseColor.png")
    normalTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_N.png")
    ormTex = common.sysUtils.copyTextureToStagePath(args.path, "Fieldstone/Fieldstone_ORM.png")

    # -------------------------------------------------------------------------
    # Geometry
    # -------------------------------------------------------------------------
    # Create all geometry up front. The material examples below can then focus only on authoring and binding materials.
    geometries = [None] * len(E)
    previewX = -2.25
    openPbrX = -0.75
    omniPbrX = 0.75
    uvwX = 2.25
    emissiveY = 1.5
    texturedY = 0.0
    glassY = -1.5
    meshHalfHeight = 0.5
    sphereRadius = 0.5
    emissiveHalfHeight = 0.15
    emissiveRadius = 0.15
    emissiveBottomZ = -0.15
    emissiveTopZ = 0.15
    meshWithGeomsubsetsZ = 0.1

    geometries[E.PREVIEW_SURFACE] = common.usdUtils.createCubeMesh(
        geometryPrim, validGeomNames[E.PREVIEW_SURFACE], meshHalfHeight, Gf.Vec3d(previewX, texturedY, 0.0)
    )
    geometries[E.OPENPBR] = common.usdUtils.createCubeMesh(
        geometryPrim, validGeomNames[E.OPENPBR], meshHalfHeight, Gf.Vec3d(openPbrX, texturedY, 0.0)
    )
    geometries[E.PREVIEW_SURFACE_GLASS] = common.usdUtils.createSphere(
        parent=geometryPrim, name=validGeomNames[E.PREVIEW_SURFACE_GLASS], radius=sphereRadius, position=Gf.Vec3d(previewX, glassY, 0.0)
    )
    geometries[E.OPENPBR_GLASS] = common.usdUtils.createSphere(
        parent=geometryPrim, name=validGeomNames[E.OPENPBR_GLASS], radius=sphereRadius, position=Gf.Vec3d(openPbrX, glassY, 0.0)
    )
    geometries[E.PREVIEW_SURFACE_EMISSIVE] = common.usdUtils.createSphere(
        parent=geometryPrim,
        name=validGeomNames[E.PREVIEW_SURFACE_EMISSIVE],
        radius=emissiveRadius,
        position=Gf.Vec3d(previewX, emissiveY, emissiveBottomZ),
    )
    geometries[E.OPENPBR_EMISSIVE] = common.usdUtils.createSphere(
        parent=geometryPrim,
        name=validGeomNames[E.OPENPBR_EMISSIVE],
        radius=emissiveRadius,
        position=Gf.Vec3d(openPbrX, emissiveY, emissiveBottomZ),
    )
    geometries[E.PREVIEW_SURFACE_EMISSIVE_TEXTURE] = common.usdUtils.createCubeMesh(
        geometryPrim,
        validGeomNames[E.PREVIEW_SURFACE_EMISSIVE_TEXTURE],
        emissiveHalfHeight,
        Gf.Vec3d(previewX, emissiveY, emissiveTopZ),
    )
    geometries[E.OPENPBR_EMISSIVE_TEXTURE] = common.usdUtils.createCubeMesh(
        geometryPrim,
        validGeomNames[E.OPENPBR_EMISSIVE_TEXTURE],
        emissiveHalfHeight,
        Gf.Vec3d(openPbrX, emissiveY, emissiveTopZ),
    )
    if includeOmniPbr:
        geometries[E.OMNIPBR] = common.usdUtils.createCubeMesh(
            geometryPrim, validGeomNames[E.OMNIPBR], meshHalfHeight, Gf.Vec3d(omniPbrX, texturedY, 0.0)
        )
        geometries[E.OMNIPBR_GLASS] = common.usdUtils.createSphere(
            parent=geometryPrim, name=validGeomNames[E.OMNIPBR_GLASS], radius=sphereRadius, position=Gf.Vec3d(omniPbrX, glassY, 0.0)
        )
        geometries[E.OMNIPBR_UVW] = common.usdUtils.createSphere(
            parent=geometryPrim, name=validGeomNames[E.OMNIPBR_UVW], radius=sphereRadius, position=Gf.Vec3d(uvwX, texturedY, 0.0)
        )
        geometries[E.OMNIPBR_EMISSIVE] = common.usdUtils.createSphere(
            parent=geometryPrim,
            name=validGeomNames[E.OMNIPBR_EMISSIVE],
            radius=emissiveRadius,
            position=Gf.Vec3d(omniPbrX, emissiveY, emissiveBottomZ),
        )
        geometries[E.OMNIPBR_EMISSIVE_TEXTURE] = common.usdUtils.createCubeMesh(
            geometryPrim,
            validGeomNames[E.OMNIPBR_EMISSIVE_TEXTURE],
            emissiveHalfHeight,
            Gf.Vec3d(omniPbrX, emissiveY, emissiveTopZ),
        )

    # Mesh with GeomSubsets: next column after omniPbrGlassSphere on the glass row.
    meshWithGeomsubsets = common.usdUtils.createMeshTabletExample(
        geometryPrim,
        validGeomNames[E.MESH_WITH_GEOMSUBSETS],
        Gf.Vec3d(uvwX, glassY, meshWithGeomsubsetsZ),
    )
    geometries[E.MESH_WITH_GEOMSUBSETS] = meshWithGeomsubsets

    # -------------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------------
    white = Gf.Vec3f(1, 1, 1)
    glassColor = Gf.Vec3f(1, 0, 0)

    # USD Preview Surface material, textures on a UV'd mesh.
    material = usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=matNames[E.PREVIEW_SURFACE], color=Gf.Vec3f(0, 1, 0.1))
    usdex.core.addColorTextureToPreviewMaterial(material, colorTex)
    usdex.core.addNormalTextureToPreviewMaterial(material, normalTex)
    usdex.core.addOrmTextureToPreviewMaterial(material, ormTex)
    usdex.core.addPreviewMaterialInterface(material)
    usdex.core.bindMaterial(geometries[E.PREVIEW_SURFACE].GetPrim(), material)

    # OpenPBR material, textures on a UV'd mesh.
    material = usdex.core.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OPENPBR], color=Gf.Vec3f(1, 1, 0))
    usdex.core.addColorTextureToPbrMaterial(material, colorTex)
    usdex.core.addOrmTextureToPbrMaterial(material, ormTex)
    usdex.core.addNormalTextureToPbrMaterial(material, normalTex)
    usdex.core.bindMaterial(geometries[E.OPENPBR].GetPrim(), material)

    if includeOmniPbr:
        # OmniPBR material, textures on a UV'd mesh.
        material = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OMNIPBR], color=Gf.Vec3f(1, 1, 0))
        usdex.rtx.addColorTextureToPbrMaterial(material, colorTex)
        usdex.rtx.addOrmTextureToPbrMaterial(material, ormTex)
        usdex.rtx.addNormalTextureToPbrMaterial(material, normalTex)
        usdex.core.bindMaterial(geometries[E.OMNIPBR].GetPrim(), material)

    # USD Preview Surface glass material on a sphere.
    material = usdex.core.defineGlassPreviewMaterial(parent=scopePrim.GetPrim(), name=matNames[E.PREVIEW_SURFACE_GLASS], color=glassColor)
    usdex.core.addPreviewMaterialInterface(material)
    usdex.core.bindMaterial(geometries[E.PREVIEW_SURFACE_GLASS].GetPrim(), material)

    # OpenPBR glass material on a sphere.
    material = usdex.core.defineGlassPbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OPENPBR_GLASS], color=glassColor)
    usdex.core.bindMaterial(geometries[E.OPENPBR_GLASS].GetPrim(), material)

    if includeOmniPbr:
        # OmniPBR glass material on a sphere.
        material = usdex.rtx.defineGlassMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OMNIPBR_GLASS], color=glassColor)
        usdex.core.bindMaterial(geometries[E.OMNIPBR_GLASS].GetPrim(), material)

        # OmniPBR material, world-space UVW projection on a UV-less sphere.
        material = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OMNIPBR_UVW], color=Gf.Vec3f(1, 1, 0))
        usdex.rtx.addColorTextureToPbrMaterial(material, colorTex)
        usdex.rtx.addOrmTextureToPbrMaterial(material, ormTex)
        usdex.rtx.addNormalTextureToPbrMaterial(material, normalTex)
        usdex.rtx.createMdlShaderInput(material, "project_uvw", True, Sdf.ValueTypeNames.Bool)
        usdex.rtx.createMdlShaderInput(material, "world_or_object", True, Sdf.ValueTypeNames.Bool)
        # The projection multiplies world-space coordinates, so this is a reciprocal of length: one texture tile per meter
        usdex.rtx.createMdlShaderInput(material, "texture_scale", Gf.Vec2f(1.0), Sdf.ValueTypeNames.Float2)
        usdex.core.bindMaterial(geometries[E.OMNIPBR_UVW].GetPrim(), material)

    # USD Preview Surface material, emissive color on a sphere.
    material = usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=matNames[E.PREVIEW_SURFACE_EMISSIVE], color=white)
    usdex.core.addEmissiveColorToPreviewMaterial(material, Gf.Vec3f(1.0, 0.77, 0.56))
    usdex.core.addPreviewMaterialInterface(material)
    usdex.core.bindMaterial(geometries[E.PREVIEW_SURFACE_EMISSIVE].GetPrim(), material)

    # OpenPBR material, emissive color on a sphere.
    material = usdex.core.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OPENPBR_EMISSIVE], color=white)
    usdex.core.addEmissiveColorToPbrMaterial(material, Gf.Vec3f(1.0, 0.77, 0.56))
    usdex.core.bindMaterial(geometries[E.OPENPBR_EMISSIVE].GetPrim(), material)

    if includeOmniPbr:
        # OmniPBR material, emissive color on a sphere.
        material = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OMNIPBR_EMISSIVE], color=white)
        usdex.rtx.addEmissiveColorToPbrMaterial(material, Gf.Vec3f(1.0, 0.77, 0.56))
        usdex.core.bindMaterial(geometries[E.OMNIPBR_EMISSIVE].GetPrim(), material)

    # USD Preview Surface material, emissive texture on a UV'd mesh.
    material = usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=matNames[E.PREVIEW_SURFACE_EMISSIVE_TEXTURE], color=white)
    usdex.core.addEmissiveTextureToPreviewMaterial(material, normalTex)
    usdex.core.addPreviewMaterialInterface(material)
    usdex.core.bindMaterial(geometries[E.PREVIEW_SURFACE_EMISSIVE_TEXTURE].GetPrim(), material)

    # OpenPBR material, emissive texture on a UV'd mesh.
    material = usdex.core.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OPENPBR_EMISSIVE_TEXTURE], color=white)
    usdex.core.addEmissiveTextureToPbrMaterial(material, normalTex)
    usdex.core.bindMaterial(geometries[E.OPENPBR_EMISSIVE_TEXTURE].GetPrim(), material)

    if includeOmniPbr:
        # OmniPBR material, emissive texture on a UV'd mesh.
        material = usdex.rtx.definePbrMaterial(parent=scopePrim.GetPrim(), name=matNames[E.OMNIPBR_EMISSIVE_TEXTURE], color=white)
        usdex.rtx.addEmissiveTextureToPbrMaterial(material, normalTex)
        usdex.core.bindMaterial(geometries[E.OMNIPBR_EMISSIVE_TEXTURE].GetPrim(), material)

    # Bind materials to the mesh's GeomSubsets.
    # fmt: off
    subsetNames = ["front", "body", "screen"]
    subsetIndices = [
        Vt.IntArray([6, 7, 8, 9]),
        Vt.IntArray([0, 1, 2, 3, 4]),
        Vt.IntArray([5]),
    ]
    # fmt: on
    geomSubsets = usdex.core.definePartitionedSubsets(meshWithGeomsubsets, subsetNames, subsetIndices)

    tabletMatNames = usdex.core.getValidChildNames(scopePrim.GetPrim(), ["tabletFront", "tabletBody", "tabletScreen"])
    subsetMaterials = [
        usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=tabletMatNames[0], color=Gf.Vec3f(0.0, 0.0, 0.0), roughness=0.0),
        usdex.core.definePreviewMaterial(
            parent=scopePrim.GetPrim(), name=tabletMatNames[1], color=Gf.Vec3f(0.6, 0.8, 0.5), metallic=1.0, roughness=0.6
        ),
        usdex.core.definePreviewMaterial(parent=scopePrim.GetPrim(), name=tabletMatNames[2], color=white, roughness=0.0),
    ]

    # Make the screen emissive
    usdex.core.addEmissiveColorToPreviewMaterial(subsetMaterials[2], white)
    for material in subsetMaterials:
        usdex.core.addPreviewMaterialInterface(material)

    usdex.core.bindMaterialSubsets(geomSubsets, subsetMaterials)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates materials using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
