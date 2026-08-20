# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import math
import pathlib
import sys

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, Kind, Sdf, Usd, UsdGeom, UsdShade


# Sample tokens
class SampleTokens:
    diffuseColor = "diffuseColor"
    bodyPaintColor = "bodyPaintColor"
    Classes = "Classes"


sampleTokens = SampleTokens()


# All constants in one organized class
class Constants:
    # Car component constants
    carDims = Gf.Vec3d(0.178, 0.0318, 0.0445)  # length, height, width in m
    carBodyColor = Gf.Vec3f(1, 0, 0)  # red
    lightBlue = Gf.Vec3f(0.3284, 0.7490, 0.7098)
    green = Gf.Vec3f(0.294, 0.725, 0)

    # Axle constants
    axleLength = 0.0254
    axleRadius = 0.0011
    axleHeadRadius = 0.003
    axleHeadLength = 0.001
    axleColor = Gf.Vec3f(0.5, 0.5, 0.75)
    axleRearOffset = 0.02
    axleFrontOffset = 0.0508

    # Wheel constants
    wheelRadius = 0.015
    wheelWidth = 0.01
    wheelColor = Gf.Vec3f(0, 0, 0)  # black

    # Track component constants
    trackDims = Gf.Vec3d(4, 1, 0.5)  # length, height, width in m
    trackRampColor = Gf.Vec3f(0.6, 0.4, 0.2)  # brown
    # Calculated constants
    trackAngle = 14.0362434679264787  # height/length in degrees (precalculated: math.degrees(math.atan(1/4)))
    trackDividerLength = math.sqrt(trackDims[0] ** 2 + trackDims[1] ** 2)


def createCarComponent(args) -> Usd.Stage:
    """Create an atomic component asset for a pinewood derby car"""
    componentName = "PinewoodDerbyCar"
    componentStageName = f"{componentName}.usda"
    stageDir = pathlib.Path(args.path).parent
    stagePath = stageDir / componentName / componentStageName

    # This is really for instructional purposes, in production asset libraries should be binary
    libraryExtension = pathlib.Path(args.path).suffix.lstrip(".")

    # Create the main asset stage with proper metadata and default prim
    assetStage = usdex.core.createStage(
        identifier=stagePath.as_posix(),
        defaultPrimName=componentName,
        upAxis=UsdGeom.Tokens.z,
        linearUnits=UsdGeom.LinearUnits.meters,
        authoringMetadata="OpenUSD Exchange Samples",
    )
    if not assetStage:
        return None

    # Create a transform for the default prim
    assetXform = usdex.core.defineXform(stage=assetStage, path=assetStage.GetDefaultPrim().GetPath())

    # Create a payload stage to hold the asset's content
    payloadStage = usdex.core.createAssetPayload(assetStage)
    if not payloadStage:
        return None

    # Create a geometry library to store reusable mesh definitions
    geometryLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getGeometryToken(), format=libraryExtension)

    # Create car body mesh
    bodyMesh = common.usdUtils.createWedge(
        geometryLibraryStage.GetDefaultPrim(), "body", length=Constants.carDims[0], width=Constants.carDims[2], height=Constants.carDims[1]
    )

    # Create a materials library to store reusable material definitions (usda format for instructional purposes)
    materialsLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getMaterialsToken(), format=libraryExtension)
    # Define materials with appropriate colors for each component
    bodyMat = usdex.core.definePreviewMaterial(
        parent=materialsLibraryStage.GetDefaultPrim(),
        name="body",
        color=Constants.carBodyColor,
        roughness=0.15,
        metallic=0.0,
    )
    # Create primvar reader for the body paint color
    usdex.core.addPrimvarShaderToPreviewMaterial(bodyMat, sampleTokens.diffuseColor, sampleTokens.bodyPaintColor)

    axleMat = usdex.core.definePreviewMaterial(
        parent=materialsLibraryStage.GetDefaultPrim(),
        name="shinyAxle",
        color=Constants.axleColor,
        roughness=0.0,
        metallic=1.0,
    )
    tireMat = usdex.core.definePreviewMaterial(
        parent=materialsLibraryStage.GetDefaultPrim(),
        name="tire",
        color=Constants.wheelColor,
        roughness=1.0,
        metallic=0.0,
    )

    # Create geometry content layer with positioned instances of our library meshes
    geometryStage = usdex.core.addAssetContent(payloadStage, usdex.core.getGeometryToken())
    geomScopePath = geometryStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getGeometryToken())
    geomScope = geometryStage.GetPrimAtPath(geomScopePath)

    # The car is offset by the wheel radius and the axle radius to ensure the wheels are on the ground when the carXform is on the ground
    carXform = usdex.core.defineXform(
        parent=geomScope.GetPrim(),
        name="pinewoodCar",
        transform=Gf.Transform(Gf.Vec3d(0, 0, Constants.wheelRadius - Constants.axleRadius * 2)),
    )
    bodyXform = usdex.core.defineXform(
        parent=carXform.GetPrim(), name="bodyOffset", transform=Gf.Transform(Gf.Vec3d(0, 0, Constants.carDims[1] * 0.5))
    )
    bodyMeshRef = usdex.core.defineReference(parent=bodyXform.GetPrim(), source=bodyMesh.GetPrim())

    # Add a class definition for the wheel-axle subcomponent
    classesScope = usdex.core.defineScope(geometryStage.GetPseudoRoot(), SampleTokens.Classes)
    classesScope.GetPrim().SetSpecifier(Sdf.SpecifierClass)

    # Make a wheel-axle subcomponent
    wheelAxleXform = usdex.core.defineXform(parent=classesScope.GetPrim(), name="wheelAxle", transform=Gf.Transform(Gf.Vec3d(0, 0, 0)))
    Usd.ModelAPI(wheelAxleXform.GetPrim()).SetKind(Kind.Tokens.subcomponent)

    axleShaft = common.usdUtils.createCylinder(
        wheelAxleXform.GetPrim(),
        "axleShaft",
        height=Constants.axleLength,
        radius=Constants.axleRadius,
        axis=UsdGeom.Tokens.y,
        displayColor=Constants.axleColor,
    )
    axleHead = common.usdUtils.createCylinder(
        wheelAxleXform.GetPrim(),
        "axleHead",
        height=Constants.axleHeadLength,
        radius=Constants.axleHeadRadius,
        axis=UsdGeom.Tokens.y,
        position=Gf.Vec3d(0, Constants.axleLength * 0.5, 0),
        displayColor=Constants.axleColor,
    )
    wheel = common.usdUtils.createCylinder(
        wheelAxleXform.GetPrim(),
        "wheel",
        height=Constants.wheelWidth,
        radius=Constants.wheelRadius,
        axis=UsdGeom.Tokens.y,
        position=Gf.Vec3d(0, Constants.wheelWidth * 0.65, 0),
        displayColor=Constants.wheelColor,
    )

    # Left front axle
    axleXform = usdex.core.defineReference(parent=bodyXform.GetPrim(), source=wheelAxleXform.GetPrim(), name="axleLeftFront")
    transform = Gf.Transform(
        Gf.Vec3d(
            Constants.carDims[0] * 0.5 - Constants.axleFrontOffset,
            Constants.carDims[2] * 0.5,
            -Constants.carDims[1] * 0.5 + Constants.axleRadius * 2,
        )
    )
    usdex.core.setLocalTransform(axleXform, transform=transform)

    # Right front axle
    axleXform = usdex.core.defineReference(parent=bodyXform.GetPrim(), source=wheelAxleXform.GetPrim(), name="axleRightFront")
    transform = Gf.Transform(
        Gf.Vec3d(
            Constants.carDims[0] * 0.5 - Constants.axleFrontOffset,
            -Constants.carDims[2] * 0.5,
            -Constants.carDims[1] * 0.5 + Constants.axleRadius * 2,
        )
    )
    transform.SetRotation(Gf.Rotation(Gf.Vec3d(0, 0, 1), -180))
    usdex.core.setLocalTransform(axleXform, transform=transform)

    # Left rear axle
    axleXform = usdex.core.defineReference(parent=bodyXform.GetPrim(), source=wheelAxleXform.GetPrim(), name="axleLeftRear")
    transform = Gf.Transform(
        Gf.Vec3d(
            -Constants.carDims[0] * 0.5 + Constants.axleRearOffset,
            Constants.carDims[2] * 0.5,
            -Constants.carDims[1] * 0.5 + Constants.axleRadius * 2,
        )
    )
    usdex.core.setLocalTransform(axleXform, transform=transform)

    # Right rear axle
    axleXform = usdex.core.defineReference(parent=bodyXform.GetPrim(), source=wheelAxleXform.GetPrim(), name="axleRightRear")
    transform = Gf.Transform(
        Gf.Vec3d(
            -Constants.carDims[0] * 0.5 + Constants.axleRearOffset,
            -Constants.carDims[2] * 0.5,
            -Constants.carDims[1] * 0.5 + Constants.axleRadius * 2,
        )
    )
    transform.SetRotation(Gf.Rotation(Gf.Vec3d(0, 0, 1), -180))
    usdex.core.setLocalTransform(axleXform, transform=transform)

    # Create materials content layer and bind materials to geometry
    materialsStage = usdex.core.addAssetContent(payloadStage, usdex.core.getMaterialsToken())
    materialScopePath = materialsStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getMaterialsToken())
    materialsScope = materialsStage.GetPrimAtPath(materialScopePath)

    # Create material references from our library
    bodyMatRef = usdex.core.defineReference(parent=materialsScope, source=bodyMat.GetPrim())
    axleMatRef = usdex.core.defineReference(parent=materialsScope, source=axleMat.GetPrim())
    tireMatRef = usdex.core.defineReference(parent=materialsScope, source=tireMat.GetPrim())

    # Apply materials to the appropriate geometric components
    bodyOverrides = materialsStage.OverridePrim(bodyMeshRef.GetPath())
    usdex.core.bindMaterial(bodyOverrides, UsdShade.Material(bodyMatRef))

    axleShaftOverrides = materialsStage.OverridePrim(axleShaft.GetPrim().GetPath())
    usdex.core.bindMaterial(axleShaftOverrides, UsdShade.Material(axleMatRef))

    axleHeadOverrides = materialsStage.OverridePrim(axleHead.GetPrim().GetPath())
    usdex.core.bindMaterial(axleHeadOverrides, UsdShade.Material(axleMatRef))

    wheelOverrides = materialsStage.OverridePrim(wheel.GetPrim().GetPath())
    usdex.core.bindMaterial(wheelOverrides, UsdShade.Material(tireMatRef))

    # Connect the payload stage to the main asset stage
    usdex.core.addAssetInterface(assetStage, payloadStage)
    if not assetStage:
        return None

    # Add asset parameterization interface, the car body paint color using a primvar (defaults to red)
    primvar = usdex.core.createConstantPrimvar(
        assetXform.GetPrim(),
        sampleTokens.bodyPaintColor,
        Constants.carBodyColor,
        Sdf.ValueTypeNames.Color3f,
    )
    if not primvar:
        print("Error creating body paint color primvar")
        return None

    primvar.GetAttr().SetDisplayName("Car Body Paint Color")

    return assetStage


def createTrackComponent(args) -> Usd.Stage:
    """Create a track component asset for a pinewood derby track"""
    componentName = "PinewoodDerbyTrack"
    componentStageName = f"{componentName}.usda"
    stageDir = pathlib.Path(args.path).parent
    stagePath = stageDir / componentName / componentStageName

    # This is really for instructional purposes, in production asset libraries should be binary
    libraryExtension = pathlib.Path(args.path).suffix.lstrip(".")

    # Create the main asset stage with proper metadata and default prim
    assetStage = usdex.core.createStage(
        identifier=stagePath.as_posix(),
        defaultPrimName=componentName,
        upAxis=UsdGeom.Tokens.z,
        linearUnits=UsdGeom.LinearUnits.meters,
        authoringMetadata="OpenUSD Exchange Samples",
    )
    if not assetStage:
        return None

    # Create a transform for the default prim
    assetXform = usdex.core.defineXform(stage=assetStage, path=assetStage.GetDefaultPrim().GetPath())

    # Create a payload stage to hold the asset's content
    payloadStage = usdex.core.createAssetPayload(assetStage)
    if not payloadStage:
        return None

    # Create a geometry library to store reusable mesh definitions
    geometryLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getGeometryToken(), format=libraryExtension)

    # Create track geometry using global constants
    rampMesh = common.usdUtils.createWedge(
        geometryLibraryStage.GetDefaultPrim(),
        "ramp",
        length=Constants.trackDims[0],
        width=Constants.trackDims[2],
        height=Constants.trackDims[1],
    )

    # Create a materials library to store reusable material definitions (usda format for instructional purposes)
    materialsLibraryStage = usdex.core.addAssetLibrary(payloadStage, usdex.core.getMaterialsToken(), format=libraryExtension)
    # Define materials with appropriate colors for each component
    rampMat = usdex.core.definePreviewMaterial(
        parent=materialsLibraryStage.GetDefaultPrim(),
        name="ramp",
        color=Constants.trackRampColor,
        roughness=0.15,
        metallic=0.0,
    )

    # Create geometry content layer with positioned instances of our library meshes
    geometryStage = usdex.core.addAssetContent(payloadStage, usdex.core.getGeometryToken())
    geomScopePath = geometryStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getGeometryToken())
    geomScope = geometryStage.GetPrimAtPath(geomScopePath)

    rampRef = usdex.core.defineReference(parent=geomScope.GetPrim(), source=rampMesh.GetPrim())
    transform = usdex.core.getLocalTransform(rampRef)
    transform.SetTranslation(Gf.Vec3d(0, 0, Constants.trackDims[1] * 0.5))
    usdex.core.setLocalTransform(rampRef, transform)

    dividers = []
    dividers.append(
        common.usdUtils.createCube(
            geomScope.GetPrim(),
            "divider",
            size=1,
            position=Gf.Vec3d(0, 0, Constants.trackDims[1] * 0.5),
            rotation=Gf.Vec3f(0, Constants.trackAngle, 0),
            scale=Gf.Vec3f(Constants.trackDividerLength, 0.02, 0.04),
        )
    )
    dividers.append(
        common.usdUtils.createCube(
            geomScope.GetPrim(),
            "divider",
            size=1,
            position=Gf.Vec3d(0, Constants.trackDims[2] * 0.5 - 0.011, Constants.trackDims[1] * 0.5),
            rotation=Gf.Vec3f(0, Constants.trackAngle, 0),
            scale=Gf.Vec3f(Constants.trackDividerLength, 0.02, 0.04),
        )
    )
    dividers.append(
        common.usdUtils.createCube(
            geomScope.GetPrim(),
            "divider",
            size=1,
            position=Gf.Vec3d(0, -Constants.trackDims[2] * 0.5 + 0.011, Constants.trackDims[1] * 0.5),
            rotation=Gf.Vec3f(0, Constants.trackAngle, 0),
            scale=Gf.Vec3f(Constants.trackDividerLength, 0.02, 0.04),
        )
    )

    # Create materials content layer and bind materials to geometry
    materialsStage = usdex.core.addAssetContent(payloadStage, usdex.core.getMaterialsToken())
    materialScopePath = materialsStage.GetDefaultPrim().GetPath().AppendChild(usdex.core.getMaterialsToken())
    materialsScope = materialsStage.GetPrimAtPath(materialScopePath)

    # Create material references from our library
    rampMatRef = usdex.core.defineReference(parent=materialsScope, source=rampMat.GetPrim())

    # Apply materials to the appropriate geometric components
    rampOverrides = materialsStage.OverridePrim(rampRef.GetPath())
    usdex.core.bindMaterial(rampOverrides, UsdShade.Material(rampMatRef))

    for divider in dividers:
        dividerOverrides = materialsStage.OverridePrim(divider.GetPath())
        usdex.core.bindMaterial(dividerOverrides, UsdShade.Material(rampMatRef))

    # Connect the payload stage to the main asset stage
    usdex.core.addAssetInterface(assetStage, payloadStage)
    if not assetStage:
        return None

    return assetStage


def createPinewoodDerbyAssembly(stage, trackComponentStage, carComponentStage) -> bool:
    transform = Gf.Transform()
    transform.SetTranslation(Gf.Vec3d(4, -6, -0.5))
    pinewoodDerbyAssembly = usdex.core.defineXform(parent=stage.GetDefaultPrim(), name="PinewoodDerbyAssembly", transform=transform)

    usdex.core.defineReference(parent=pinewoodDerbyAssembly.GetPrim(), source=trackComponentStage.GetDefaultPrim(), name="Track")

    car0Prim = usdex.core.defineReference(parent=pinewoodDerbyAssembly.GetPrim(), source=carComponentStage.GetDefaultPrim(), name="BlueCar")
    if not usdex.core.setConstantPrimvar(car0Prim.GetPrim(), sampleTokens.bodyPaintColor, Constants.lightBlue):
        return False

    car1Prim = usdex.core.defineReference(parent=pinewoodDerbyAssembly.GetPrim(), source=carComponentStage.GetDefaultPrim(), name="GreenCar")
    if not usdex.core.setConstantPrimvar(car1Prim.GetPrim(), sampleTokens.bodyPaintColor, Constants.green):
        return False

    # Place the cars on the track (at the start with the appropriate spacing and rotation)
    carOffsetFromBackOfTrack = Constants.carDims[0] * 0.5 - Constants.trackDims[0] * 0.5
    carHeight = Constants.trackDims[1]
    carDropHeight = Constants.carDims[0] * 0.5 * math.tan(math.radians(Constants.trackAngle))
    carLaneOffset = Constants.trackDims[2] * 0.25

    transform = Gf.Transform()
    transform.SetTranslation(Gf.Vec3d(carOffsetFromBackOfTrack, -carLaneOffset, carHeight - carDropHeight))
    transform.SetRotation(Gf.Rotation(Gf.Vec3d(0, 1, 0), Constants.trackAngle))
    usdex.core.setLocalTransform(car0Prim, transform=transform)

    transform.SetTranslation(Gf.Vec3d(carOffsetFromBackOfTrack, carLaneOffset, carHeight - carDropHeight))
    transform.SetRotation(Gf.Rotation(Gf.Vec3d(0, 1, 0), Constants.trackAngle))
    usdex.core.setLocalTransform(car1Prim, transform=transform)

    usdex.core.configureAssemblyHierarchy(pinewoodDerbyAssembly.GetPrim())
    return True


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    # Set the default prim to group kind to allow assembly (Model) children
    Usd.ModelAPI(stage.GetDefaultPrim()).SetKind(Kind.Tokens.group)

    carComponentStage = createCarComponent(args)
    trackComponentStage = createTrackComponent(args)
    if not carComponentStage or not trackComponentStage:
        print("Error creating component stages, exiting")
        sys.exit(-1)

    print(f"Car Component: {carComponentStage.GetRootLayer().identifier}")
    print(f"Track Component: {trackComponentStage.GetRootLayer().identifier}")

    if not createPinewoodDerbyAssembly(stage, trackComponentStage, carComponentStage):
        print("Error creating assembly, exiting")
        sys.exit(-1)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates an assembly hierarchy using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
