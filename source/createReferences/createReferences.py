# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from pxr import Gf, Usd, UsdGeom


def createComponentStage(args) -> str:
    """Create a stage with a 2x2x2 grouping of mesh cubes"""
    componentName = "Cube_2x2x2"
    stageDir = pathlib.Path(args.path).parent
    extension = pathlib.Path(args.path).suffix
    stagePath = stageDir / str(componentName + extension)

    # Create a USD component stage in memory, ensuring that key metadata is set
    componentStage = Usd.Stage.CreateInMemory()
    if not componentStage:
        return ""

    usdex.core.configureStage(
        stage=componentStage,
        defaultPrimName=componentName,
        upAxis=UsdGeom.GetFallbackUpAxis(),
        linearUnits=UsdGeom.LinearUnits.centimeters,
        authoringMetadata="OpenUSD Exchange Samples",
    )

    # Define the defaultPrim as Xform (it was originally created as a Scope)
    xform = usdex.core.defineXform(
        stage=componentStage,
        path=componentStage.GetDefaultPrim().GetPath(),
    )

    # Create 8 cubes in a 2x2x2 grid
    cubeSize = 25
    cubeSpacing = 30
    offset = -(cubeSize + (cubeSpacing - cubeSize) / 2)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                cubeName = f"Cube_{i}_{j}_{k}"
                pos = Gf.Vec3d(
                    i * (cubeSize + cubeSpacing) + offset,
                    j * (cubeSize + cubeSpacing) + offset,
                    k * (cubeSize + cubeSpacing) + offset,
                )
                common.usdUtils.createCubeMesh(parent=componentStage.GetDefaultPrim(), meshName=cubeName, halfHeight=cubeSize, localPos=pos)

    # Write the component stage to disk
    success = usdex.core.exportLayer(
        layer=componentStage.GetRootLayer(),
        identifier=stagePath.as_posix(),
        authoringMetadata=common.usdUtils.getSamplesAuthoringMetadata(),
        comment=f"{componentName} component",
        fileFormatArgs=args.fileFormatArgs,
    )
    if not success:
        return ""

    return stagePath.as_posix()


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    defaultPrim = stage.GetDefaultPrim()

    componentStagePath = createComponentStage(args)
    if not len(componentStagePath):
        print("Error creating component stage, exiting")
        sys.exit(-1)

    print(f"Component stage: {componentStagePath}")

    # Make a relative path from the stage's folder to the component's stage
    relativeComponentPath = pathlib.Path(componentStagePath).relative_to(pathlib.Path(args.path).parent)
    referencePath = f"./{relativeComponentPath.as_posix()}"

    # Create a reference prim
    primNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["referencePrim"])
    refTransform = Gf.Transform()
    refTransform.SetTranslation(Gf.Vec3d(0, 2.5, 300))
    xform = usdex.core.defineXform(parent=defaultPrim, name=primNames[0], transform=refTransform)
    xform.GetPrim().GetReferences().AddReference(referencePath)
    # Override the mesh scale from the reference
    xformable = UsdGeom.Xformable(xform.GetPrim().GetChildren()[-1])
    if xformable:
        transform = usdex.core.getLocalTransform(xformable.GetPrim())
        transform.SetScale(Gf.Vec3d(0.5))
        usdex.core.setLocalTransform(xformable.GetPrim(), transform)

    # Create a payload prim
    primNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["payloadPrim"])
    refTransform.SetTranslation(Gf.Vec3d(300, 2.5, 0))
    xform = usdex.core.defineXform(parent=defaultPrim, name=primNames[0], transform=refTransform)
    xform.GetPrim().GetPayloads().AddPayload(referencePath)
    # Override the mesh constant color primvar from the payload
    mesh = UsdGeom.Mesh(xform.GetPrim().GetChildren()[-1])
    if mesh:
        color = [Gf.Vec3f(0.3, 0, 1)]
        primvar = mesh.GetDisplayColorPrimvar()
        usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, color).setPrimvar(primvar)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a reference and payload using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
