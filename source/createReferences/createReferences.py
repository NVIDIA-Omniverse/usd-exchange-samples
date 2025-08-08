# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


def createComponentStage(args) -> Usd.Stage:
    """Create a stage with a 2x2x2 grouping of mesh cubes"""
    componentName = "Cube_2x2x2"
    stageDir = pathlib.Path(args.path).parent
    extension = pathlib.Path(args.path).suffix
    stagePath = stageDir / str(componentName + extension)

    # Create a USD component stage in memory, ensuring that key metadata is set
    componentStage = Usd.Stage.CreateInMemory()
    if not componentStage:
        return None

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
        return None

    return Usd.Stage.Open(stagePath.as_posix())


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    defaultPrim = stage.GetDefaultPrim()

    componentStage = createComponentStage(args)
    if not componentStage:
        print("Error creating component stage, exiting")
        sys.exit(-1)

    print(f"Component stage: {componentStage.GetRootLayer().identifier}")

    # Create a reference prim
    primNames = usdex.core.getValidChildNames(stage.GetDefaultPrim(), ["referencePrim", "payloadPrim"])
    refTransform = Gf.Transform()
    refTransform.SetTranslation(Gf.Vec3d(0, 2.5, 300))
    prim = usdex.core.defineReference(parent=defaultPrim, source=componentStage.GetDefaultPrim(), name=primNames[0])
    xform = UsdGeom.Xform(prim)
    usdex.core.setLocalTransform(xform, refTransform)

    # Override the mesh scale from the reference
    xformable = UsdGeom.Xformable(xform.GetPrim().GetChildren()[-1])
    if xformable:
        transform = usdex.core.getLocalTransform(xformable)
        transform.SetScale(Gf.Vec3d(0.5))
        usdex.core.setLocalTransform(xformable, transform)

    # Create a payload prim
    refTransform.SetTranslation(Gf.Vec3d(300, 2.5, 0))
    prim = usdex.core.definePayload(parent=defaultPrim, source=componentStage.GetDefaultPrim(), name=primNames[1])
    xform = UsdGeom.Xform(prim)
    usdex.core.setLocalTransform(xform, refTransform)

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
