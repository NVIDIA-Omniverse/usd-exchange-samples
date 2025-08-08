# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import pathlib
import sys

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Kind, Tf, Usd, UsdGeom, UsdShade


def createAsset(args) -> Usd.Stage:
    """Create an atomic component asset for a flower planter with 3 flowers"""
    componentStageName = "FlowerPlanter.usda"
    stageDir = pathlib.Path(args.path).parent
    stagePath = stageDir / componentStageName

    # Create the main asset stage with proper metadata and default prim
    assetStage = usdex.core.createStage(
        identifier=stagePath.as_posix(),
        defaultPrimName="FlowerPlanter",
        upAxis=UsdGeom.Tokens.y,
        linearUnits=UsdGeom.LinearUnits.centimeters,
        authoringMetadata="OpenUSD Exchange Samples",
    )
    if not assetStage:
        return None

    # Create a transform for the default prim and set its display name
    assetXform = usdex.core.defineXform(stage=assetStage, path=assetStage.GetDefaultPrim().GetPath())
    usdex.core.setDisplayName(assetXform.GetPrim(), "🌻")

    # Create a payload stage to hold the asset's content
    payloadStage = usdex.core.createAssetPayload(assetStage)
    if not payloadStage:
        return None

    # Create a geometry library to store reusable mesh definitions
    geometryLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getGeometryToken())

    # Define the basic geometric shapes for our flower components
    planterLibraryGeom = common.usdUtils.createCylinder(
        geometryLibraryStage.GetDefaultPrim(), "Planter", height=10, radius=15
    )  # Larger planter for 3 flowers
    stemLibraryGeom = common.usdUtils.createCylinder(geometryLibraryStage.GetDefaultPrim(), "Stem", height=20, radius=1)
    petalLibraryGeom = common.usdUtils.createCylinder(geometryLibraryStage.GetDefaultPrim(), "Petal", height=2.5, radius=8)

    # Create a materials library to store reusable material definitions
    materialsLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getMaterialsToken())
    # Define materials with appropriate colors for each component
    clayLibraryMat = usdex.core.definePreviewMaterial(parent=materialsLibraryStage.GetDefaultPrim(), name="Clay", color=Gf.Vec3f(0.7, 0.44, 0.24))
    greenStemLibraryMat = usdex.core.definePreviewMaterial(parent=materialsLibraryStage.GetDefaultPrim(), name="GreenStem", color=Gf.Vec3f(0, 1, 0))
    yellowPetalsLibraryMat = usdex.core.definePreviewMaterial(
        parent=materialsLibraryStage.GetDefaultPrim(), name="YellowPetals", color=Gf.Vec3f(1, 0.85, 0.1)
    )

    # Create geometry content layer with positioned instances of our library meshes
    geometryStage = usdex.core.addAssetContent(payloadStage, usdex.core.getGeometryToken())
    geomScopePath = geometryStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getGeometryToken())
    geomScope = geometryStage.GetPrimAtPath(geomScopePath)

    # Create a hierarchical structure for the flower planter components using Xform nodes
    flowerPlanterXform = usdex.core.defineXform(parent=geomScope, name="FlowerPlanterStructure")

    # Single planter at the base (shared by all flowers)
    planterRef = usdex.core.defineReference(parent=flowerPlanterXform.GetPrim(), source=planterLibraryGeom.GetPrim())
    usdex.core.setLocalTransform(
        prim=planterRef,
        translation=Gf.Vec3d(0, 5, 0),  # Position planter at ground level
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0, 0, 0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    numFlowers = 3

    # Create a vector of flower names
    flowerNames = usdex.core.getValidChildNames(flowerPlanterXform.GetPrim(), ["Flower"] * numFlowers)

    # Create 3 flowers with different positions
    flowerPositions = [
        Gf.Vec3d(-8, 0, 0),  # Left flower
        Gf.Vec3d(0, 0, 0),  # Center flower
        Gf.Vec3d(8, 0, 0),  # Right flower
    ]

    flowerRotation = [
        Gf.Vec3f(0, 0, 30),
        Gf.Vec3f(0, 0, 0),
        Gf.Vec3f(0, 0, -30),
    ]

    for i, position in enumerate(flowerPositions):
        flowerName = flowerNames[i]

        # Create Xform for each flower's stem positioning
        flowerXform = usdex.core.defineXform(parent=flowerPlanterXform.GetPrim(), name=flowerName)
        stemXform = usdex.core.defineXform(parent=flowerXform.GetPrim(), name="StemXform")
        usdex.core.setLocalTransform(
            prim=stemXform.GetPrim(),
            translation=Gf.Vec3d(position[0], 15, position[2]),  # Position stem relative to planter top
            pivot=Gf.Vec3d(0.0),
            rotation=flowerRotation[i],
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
        )
        # Stem positioned relative to planter
        usdex.core.defineReference(parent=stemXform.GetPrim(), source=stemLibraryGeom.GetPrim())

        # Create Xform for petals positioning
        petalXform = usdex.core.defineXform(parent=stemXform.GetPrim(), name="PetalXform")
        usdex.core.setLocalTransform(
            prim=petalXform.GetPrim(),
            translation=Gf.Vec3d(0, 10, 0),  # Position petals relative to stem top
            pivot=Gf.Vec3d(0.0),
            rotation=Gf.Vec3f(90, 0, 0),  # Rotate petals to face outward
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
        )
        # Petals positioned relative to stem
        usdex.core.defineReference(parent=petalXform.GetPrim(), source=petalLibraryGeom.GetPrim())

    # Create materials content layer and bind materials to geometry
    materialsStage = usdex.core.addAssetContent(payloadStage, usdex.core.getMaterialsToken())
    materialScopePath = materialsStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getMaterialsToken())
    materialsScope = materialsStage.GetPrimAtPath(materialScopePath)

    # Create material references from our library
    clayRef = usdex.core.defineReference(parent=materialsScope, source=clayLibraryMat.GetPrim())
    greenStemRef = usdex.core.defineReference(parent=materialsScope, source=greenStemLibraryMat.GetPrim())
    yellowPetalsRef = usdex.core.defineReference(parent=materialsScope, source=yellowPetalsLibraryMat.GetPrim())

    # Apply materials to the appropriate geometric components
    planterOverrides = materialsStage.OverridePrim(planterRef.GetPath())
    usdex.core.bindMaterial(planterOverrides, UsdShade.Material(clayRef))

    # Apply materials to all stems and petals
    flowerPlanterStructurePath = geomScopePath.AppendChild("FlowerPlanterStructure")
    for i in range(numFlowers):
        flowerName = flowerNames[i]
        flowerXformPath = flowerPlanterStructurePath.AppendChild(flowerName)
        stemXformPath = flowerXformPath.AppendChild("StemXform")
        petalXformPath = stemXformPath.AppendChild("PetalXform")
        stemPath = stemXformPath.AppendChild("Stem")
        petalPath = petalXformPath.AppendChild("Petal")

        stemOverrides = materialsStage.OverridePrim(stemPath)
        petalOverrides = materialsStage.OverridePrim(petalPath)

        if stemOverrides:
            usdex.core.bindMaterial(stemOverrides, UsdShade.Material(greenStemRef))
        if petalOverrides:
            usdex.core.bindMaterial(petalOverrides, UsdShade.Material(yellowPetalsRef))

    # Connect the payload stage to the main asset stage
    usdex.core.addAssetInterface(assetStage, payloadStage)
    if not assetStage:
        return None

    return assetStage


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    defaultPrim = stage.GetDefaultPrim()

    # Set the World prim to assembly kind to allow component children
    Usd.ModelAPI(defaultPrim).SetKind(Kind.Tokens.assembly)

    assetStage = createAsset(args)
    if not assetStage:
        print("Error creating asset stage, exiting")
        sys.exit(-1)

    print(f"Asset stage: {assetStage.GetRootLayer().identifier}")

    # Create a reference to the asset
    refTransform = Gf.Transform()
    refTransform.SetTranslation(Gf.Vec3d(-300, -50, 300))
    refTransform.SetScale(Gf.Vec3d(5))
    prim = usdex.core.defineReference(parent=defaultPrim, source=assetStage.GetDefaultPrim(), name="FlowerPlanter")
    xform = UsdGeom.Xform(prim)
    usdex.core.setLocalTransform(xform, refTransform)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates an atomic model asset using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
