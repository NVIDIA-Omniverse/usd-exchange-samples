# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import traceback
from typing import Optional

import usdex.core
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdUtils


def getSamplesAuthoringMetadata():
    return "OpenUSD Exchange Samples"


def openOrCreateStage(identifier: str, defaultPrimName: str = "World", fileFormatArgs: Optional[dict] = None) -> Optional[Usd.Stage]:
    """Open or create a USD stage

    Args:
        identifier (str): The identifier (file path) for the stage
        defaultPrimName (str, optional): The default prim name. Defaults to "World"
        fileFormatArgs (dict, optional): File format args if the stage doesn't already exist

    Returns:
        Usd.Stage: The opened or created stage
    """
    # Activate the SDK's diagnostic delegate to set the default level to "Warning" to hide "Status" messages
    usdex.core.activateDiagnosticsDelegate()
    # Attempt to open the layer first because this doesn't issue a runtime error
    layer = Sdf.Layer.FindOrOpen(identifier)
    stage = None
    try:
        if not layer:
            # Create/overwrite a USD stage, ensuring that key metadata is set
            # NOTE: Samples use Z-up (UsdGeom.Tokens.z)
            fileFormatArgs = fileFormatArgs or dict()
            stage = usdex.core.createStage(
                identifier=identifier,
                defaultPrimName=defaultPrimName,
                upAxis=UsdGeom.Tokens.z,
                linearUnits=UsdGeom.LinearUnits.meters,
                authoringMetadata=getSamplesAuthoringMetadata(),
                fileFormatArgs=fileFormatArgs,
            )
        else:
            stage = Usd.Stage.Open(identifier)
    except Tf.ErrorException:
        print(traceback.format_exc())

    return stage


def packageStageAsUsdz(stage: Usd.Stage, usdzPath: str) -> bool:
    """Package a saved stage and its dependencies into a USDZ archive."""
    if not stage:
        print("Error packaging USDZ: invalid stage")
        return False

    rootLayer = stage.GetRootLayer()
    rootLayerPath = rootLayer.realPath or rootLayer.identifier
    if not rootLayerPath:
        print("Error packaging USDZ: stage root layer has no file path")
        return False

    rootLayerPathObj = pathlib.Path(rootLayerPath).resolve()
    usdzPathObj = pathlib.Path(usdzPath).resolve()
    asset = Sdf.AssetPath(rootLayerPathObj.as_posix())
    try:
        if not UsdUtils.CreateNewUsdzPackage(asset, usdzPathObj.as_posix()):
            usdzPathObj.unlink(missing_ok=True)
            print(f"Error creating USDZ package: {usdzPath}")
            return False
    except Tf.ErrorException as exc:
        print(exc)
        usdzPathObj.unlink(missing_ok=True)
        print(f"Error creating USDZ package: {usdzPath}")
        return False

    print(f"Created USDZ package: {usdzPath}")
    return True


def saveStage(stage: Usd.Stage, authoringMetadata: str, usdzPath: Optional[str] = None) -> bool:
    """Save a stage and optionally package it as USDZ."""
    usdex.core.saveStage(stage, authoringMetadata)
    if usdzPath:
        return packageStageAsUsdz(stage, usdzPath)
    return True


def setOmniverseRefinement(prim: Usd.Prim, enabled: bool = True, level: int = 2):
    """Set custom attributes for curved geom prim refinement in NVIDIA Omniverse RTX"""
    attr = prim.CreateAttribute(name="refinementEnableOverride", typeName=Sdf.ValueTypeNames.Bool, custom=True)
    attr.Set(enabled)
    attr.SetDisplayName("omniRefinementEnableOverride")
    attr = prim.CreateAttribute(name="refinementLevel", typeName=Sdf.ValueTypeNames.Int, custom=True)
    attr.Set(level)
    attr.SetDisplayName("omniRefinementLevel")


def setExtents(prim: UsdGeom.Boundable):
    """Compute and set the extents on a prim"""
    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(prim, Usd.TimeCode.Default())
    prim.GetExtentAttr().Set(extent)


def setTransform(
    prim: Usd.Prim,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
):
    """Set the transform of a prim

    Args:
        prim (Usd.Prim): The prim to set the transform and display color of
        position (Gf.Vec3d, optional): The position of the prim. Defaults to None
        rotation (Gf.Vec3f, optional): The rotation of the prim. Defaults to None
        scale (Gf.Vec3f, optional): The scale of the prim. Defaults to None
    """
    if position is not None or rotation is not None or scale is not None:
        pivotValue = Gf.Vec3d(0)
        positionValue = position or Gf.Vec3d(0)
        rotationValue = rotation or Gf.Vec3f(0)
        scaleValue = scale or Gf.Vec3f(1)
        usdex.core.setLocalTransform(prim, positionValue, pivotValue, rotationValue, usdex.core.RotationOrder.eXyz, scaleValue)


def createSphere(
    parent: Usd.Prim,
    name: str = "sphere",
    radius: float = 0.5,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
    displayColor: Gf.Vec3f = None,
) -> UsdGeom.Sphere:
    """Create a sphere prim as a child of the parent prim

    Args:
        parent (Usd.Prim): The parent prim to create the sphere under
        name (str): The proposed name of the sphere prim
        radius (float, optional): The radius of the sphere. Defaults to 0.5
        position (Gf.Vec3d, optional): The position of the sphere. Defaults to None
        rotation (Gf.Vec3f, optional): The rotation of the sphere. Defaults to None
        scale (Gf.Vec3f, optional): The scale of the sphere. Defaults to None
        displayColor (Gf.Vec3f, optional): The display color of the sphere. Defaults to None

    Returns:
        UsdGeom.Sphere: The created sphere prim
    """
    validToken = usdex.core.getValidChildName(parent, name)
    sphere = usdex.core.defineSphere(parent, validToken, radius, displayColor)
    setOmniverseRefinement(sphere.GetPrim())

    # Set transform.
    setTransform(sphere.GetPrim(), position, rotation, scale)

    return sphere


def createCube(
    parent: Usd.Prim,
    name: str = "cube",
    size: float = 1,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
    displayColor: Gf.Vec3f = None,
) -> UsdGeom.Cube:
    """Create a cube prim as a child of the parent prim

    Args:
        parent (Usd.Prim): The parent prim to create the cube under
        name (str): The proposed name of the cube prim
        size (float, optional): The size of the cube. Defaults to 1
        position (Gf.Vec3d, optional): The position of the cube. Defaults to None
        rotation (Gf.Vec3f, optional): The rotation of the cube. Defaults to None
        scale (Gf.Vec3f, optional): The scale of the cube. Defaults to None
        displayColor (Gf.Vec3f, optional): The display color of the cube. Defaults to None

    Returns:
        UsdGeom.Cube: The created cube prim
    """
    # Get a valid, unique child prim name under the parent prim
    validToken = usdex.core.getValidChildName(parent, name)
    cube = usdex.core.defineCube(parent, validToken, size, displayColor)

    # Set transform.
    setTransform(cube.GetPrim(), position, rotation, scale)

    return cube


def createCone(
    parent: Usd.Prim,
    name: str = "cone",
    axis: str = UsdGeom.Tokens.z,
    height: float = 1,
    radius: float = 0.5,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
    displayColor: Gf.Vec3f = None,
) -> UsdGeom.Cone:
    """Create a UsdGeom.Cone prim with Omniverse refinement and extents

    Args:
        parent (Usd.Prim): The parent prim to create the cone under
        name (str, optional): The proposed name of the cone prim. Defaults to "cone"
        axis (str, optional): The axis along which the cone is aligned. Defaults to UsdGeom.Tokens.z
        height (float, optional): The height of the cone. Defaults to 1
        radius (float, optional): The radius of the cone. Defaults to 0.5
        position (Gf.Vec3d, optional): The position of the cone. Defaults to None
        rotation (Gf.Vec3f, optional): The rotation of the cone. Defaults to None
        scale (Gf.Vec3f, optional): The scale of the cone. Defaults to None
        displayColor (Gf.Vec3f, optional): The display color of the cone. Defaults to None

    Returns:
        UsdGeom.Cone: The created cone prim
    """
    validToken = usdex.core.getValidChildName(parent, name)
    cone = usdex.core.defineCone(parent, validToken, radius, height, axis, displayColor)
    setOmniverseRefinement(cone.GetPrim())

    # Set transform.
    setTransform(cone.GetPrim(), position, rotation, scale)

    return cone


def createCylinder(
    parent: Usd.Prim,
    name: str = "cylinder",
    axis: str = UsdGeom.Tokens.z,
    height: float = 4,
    radius: float = 0.5,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
    displayColor: Gf.Vec3f = None,
) -> UsdGeom.Cylinder:
    """Create a UsdGeom.Cylinder as a child of the parent prim with Omniverse refinement and extents

    Args:
        parent (Usd.Prim): The parent prim to create the cylinder under
        name (str, optional): The proposed name of the cylinder prim. Defaults to "cylinder"
        axis (str, optional): The axis along which the cylinder is aligned. Defaults to UsdGeom.Tokens.z
        height (float, optional): The height of the cylinder. Defaults to 4
        radius (float, optional): The radius of the cylinder. Defaults to 0.5
        position (Gf.Vec3d, optional): The position of the cylinder. Defaults to None
        rotation (Gf.Vec3f, optional): The rotation of the cylinder. Defaults to None
        scale (Gf.Vec3f, optional): The scale of the cylinder. Defaults to None
        displayColor (Gf.Vec3f, optional): The display color of the cylinder. Defaults to None

    Returns:
        UsdGeom.Cone: The created cylinder prim
    """
    validToken = usdex.core.getValidChildName(parent, name)
    cylinder = usdex.core.defineCylinder(parent, validToken, radius, height, axis, displayColor)
    setOmniverseRefinement(cylinder.GetPrim())

    # Set transform.
    setTransform(cylinder.GetPrim(), position, rotation, scale)

    return cylinder


def createCapsule(
    parent: Usd.Prim,
    name: str = "capsule",
    axis: str = UsdGeom.Tokens.z,
    height: float = 1,
    radius: float = 0.5,
    position: Gf.Vec3d = None,
    rotation: Gf.Vec3f = None,
    scale: Gf.Vec3f = None,
    displayColor: Gf.Vec3f = None,
) -> UsdGeom.Capsule:
    """Create a UsdGeom.Capsule as a child of the parent prim with Omniverse refinement and extents

    Args:
        parent (Usd.Prim): The parent prim to create the capsule under
        name (str, optional): The proposed name of the capsule prim. Defaults to "capsule"
        axis (str, optional): The axis along which the capsule is aligned. Defaults to UsdGeom.Tokens.z
        height (float, optional): The height of the capsule. Defaults to 1
        radius (float, optional): The radius of the capsule. Defaults to 0.5

    Returns:
        UsdGeom.Capsule: The created capsule prim
    """
    validToken = usdex.core.getValidChildName(parent, name)
    capsule = usdex.core.defineCapsule(parent, validToken, radius, height, axis, displayColor)
    setOmniverseRefinement(capsule.GetPrim())

    # Set transform.
    setTransform(capsule.GetPrim(), position, rotation, scale)

    return capsule


def createCubeMesh(parent: str, meshName: str = "cubeMesh", halfHeight: float = 0.5, localPos: Gf.Vec3d = Gf.Vec3d(0.0)) -> UsdGeom.Mesh:
    """
    Creates a cube mesh with the specified half height and local position

    Args:
        parent (str): The parent prim for the new cube mesh
        meshName (str, optional): The name of the mesh. Defaults to "cubeMesh"
        halfHeight (float, optional): The half height of the cube. Defaults to 0.5
        localPos (Gf.Vec3d, optional): The local position of the cube. Defaults to 0,0,0

    Returns:
        UsdGeom.Mesh: The created cube mesh
    """
    # fmt: off
    h = halfHeight
    faceVertexIndices = [
        0, 1, 2, 1, 3, 2,
        4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11,
        12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19,
        20, 21, 22, 20, 22, 23,
    ]
    faceVertexCounts = [3] * 12
    normals = [
        (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
        (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
        (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
        (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
        (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
        (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
    ]
    points = [
        (h, h, -h), (-h, h, -h), (h, h, h), (-h, h, h),
        (h, -h, h), (-h, -h, h), (-h, -h, -h), (h, -h, -h),
        (h, -h, -h), (-h, -h, -h), (-h, h, -h), (h, h, -h),
        (h, -h, h), (h, -h, -h), (h, h, -h), (h, h, h),
        (-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h),
        (-h, -h, -h), (-h, -h, h), (-h, h, h), (-h, h, -h),
    ]
    uvs = [
        (0, 0), (0, 1), (1, 1), (1, 0),
        (0, 0), (0, 1), (1, 1), (1, 0),
        (0, 0), (0, 1), (1, 1), (1, 0),
        (0, 0), (0, 1), (1, 1), (1, 0),
        (0, 0), (0, 1), (1, 1), (1, 0),
        (0, 0), (0, 1), (1, 1), (1, 0),
    ]
    # fmt: on

    # Get a valid mesh path
    meshPrimNames = usdex.core.getValidChildNames(parent, [meshName])
    if meshPrimNames[0] != meshName:
        print(f"Renaming input mesh name <{meshName}> to the valid USD prim name <{meshPrimNames[0]}>")
    meshPrimPath = parent.GetPath().AppendChild(meshPrimNames[0])

    # Index the normals and UVs
    normalsPrimvarData = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.vertex, normals)
    normalsPrimvarData.index()
    uvsPrimvarData = usdex.core.Vec2fPrimvarData(UsdGeom.Tokens.vertex, uvs)
    uvsPrimvarData.index()

    # Create the mesh
    meshPrim = usdex.core.definePolyMesh(
        stage=parent.GetStage(),
        path=meshPrimPath,
        faceVertexCounts=faceVertexCounts,
        faceVertexIndices=faceVertexIndices,
        points=points,
        normals=normalsPrimvarData,
        uvs=uvsPrimvarData,
        displayColor=usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, [Gf.Vec3f(0.463, 0.725, 0.0)]),
    )
    if not meshPrim:
        return meshPrim

    # Set the display name if the input name was not "valid", the display name can handle UTF-8 characters
    if meshPrimNames[0] != meshName:
        usdex.core.setDisplayName(meshPrim.GetPrim(), meshName)

    # Set initial transformation if localPos != 0,0,0
    if localPos != Gf.Vec3d(0.0):
        usdex.core.setLocalTransform(
            xformable=meshPrim,
            translation=localPos,
            pivot=Gf.Vec3d(0.0),
            rotation=Gf.Vec3f(0.0),
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
            time=Usd.TimeCode.Default(),
        )

    return meshPrim


def createWedge(
    parent: Usd.Prim, meshName: str = "wedgeMesh", height: float = 1.0, length: float = 1.0, width: float = 1.0, localPos: Gf.Vec3d = Gf.Vec3d(0.0)
) -> UsdGeom.Mesh:
    """
    Creates a wedge mesh (triangular prism) with the specified dimensions and local position

    Args:
        parent (Usd.Prim): The parent prim for the new wedge mesh
        meshName (str, optional): The name of the mesh. Defaults to "wedgeMesh"
        height (float, optional): The height scale of the wedge. Defaults to 1.0
        length (float, optional): The length scale of the wedge. Defaults to 1.0
        width (float, optional): The width scale of the wedge. Defaults to 1.0
        localPos (Gf.Vec3d, optional): The local position of the wedge. Defaults to 0,0,0

    Returns:
        UsdGeom.Mesh: The created wedge mesh
    """
    h = 0.5

    # fmt: off
    # Wedge vertex indices and counts
    # 5 faces: 3 triangular (3 vertices each), 2 rectangular (4 vertices each)
    faceVertexIndices = [
        0, 2, 4,
        1, 0, 4, 5,
        5, 4, 2, 3,
        3, 1, 5,
        3, 2, 0, 1
    ]
    faceVertexCounts = [3, 4, 4, 3, 4]

    # Normals for each face vertex (18 normals total)
    normals = [
        (0, -1, 0), (0, -1, 0), (0, -1, 0),  # Face 1 (3 vertices)
        (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),  # Face 2 (4 vertices)
        (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),  # Face 3 (4 vertices)
        (0, 1, 0), (0, 1, 0), (0, 1, 0),  # Face 4 (3 vertices)
        (0.70710677, 0, 0.70710677), (0.70710677, 0, 0.70710677), (0.70710677, 0, 0.70710677), (0.70710677, 0, 0.70710677),  # Face 5 (4 vertices)
    ]

    # Wedge points (6 vertices total)
    # Scale the reference points to match our dimensions
    points = [
        (h, -h, -h),  # Vertex 0: (1, -1, -1) scaled
        (h, h, -h),  # Vertex 1: (1, 1, -1) scaled
        (-h, -h, h),  # Vertex 2: (-1, -1, 1) scaled
        (-h, h, h),  # Vertex 3: (-1, 1, 1) scaled
        (-h, -h, -h),  # Vertex 4: (-1, -1, -1) scaled
        (-h, h, -h),  # Vertex 5: (-1, 1, -1) scaled
    ]
    # fmt: on

    # Get a valid mesh path
    meshPrimName = usdex.core.getValidChildName(parent, meshName)
    if meshPrimName != meshName:
        print(f"Renaming input mesh name <{meshName}> to the valid USD prim name <{meshPrimName}>")

    # Index the normals
    normalsPrimvarData = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.faceVarying, normals)
    normalsPrimvarData.index()

    # Create the mesh
    meshPrim = usdex.core.definePolyMesh(
        parent=parent,
        name=meshPrimName,
        faceVertexCounts=faceVertexCounts,
        faceVertexIndices=faceVertexIndices,
        points=points,
        normals=normalsPrimvarData,
        displayColor=usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, [Gf.Vec3f(1, 0, 0)]),
    )
    if not meshPrim:
        return meshPrim

    # Set the display name if the input name was not "valid", the display name can handle UTF-8 characters
    if meshPrimName != meshName:
        usdex.core.setDisplayName(meshPrim.GetPrim(), meshName)

    # Set initial transformation
    usdex.core.setLocalTransform(
        xformable=meshPrim,
        translation=localPos,
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0.0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(length, width, height),
        time=Usd.TimeCode.Default(),
    )

    return meshPrim


def createMeshTabletExample(
    parent: Usd.Prim,
    meshName: str = "meshWithGeomsubsets",
    localPos: Gf.Vec3d = Gf.Vec3d(0.0),
) -> UsdGeom.Mesh:
    """Creates a tablet-like mesh used by the createMaterials GeomSubset example.

    Face partitions for material binding are authored separately with
    ``definePartitionedSubsets``.

    Args:
        parent: The parent prim for the new mesh
        meshName: The name of the mesh. Defaults to "meshWithGeomsubsets"
        localPos: The local position of the mesh. Defaults to 0,0,0

    Returns:
        UsdGeom.Mesh: The created mesh
    """
    # fmt: off
    faceVertexCounts = [4] * 10
    faceVertexIndices = [
        0, 1, 3, 2, 2, 3, 7, 6, 6, 7, 5, 4, 4, 5, 1, 0,
        2, 6, 4, 0, 8, 9, 10, 11, 9, 8, 7, 3, 10, 9, 3, 1,
        11, 10, 1, 5, 8, 11, 5, 7,
    ]
    # Uniform normals: one normal per face (collapsed from faceVarying source data).
    normals = [
        (-1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 1, 0),
        (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
    ]
    points = [
        (-0.25, 0.0525, -0.4), (-0.25, 0.0025, -0.4), (-0.25, 0.0525, 0.4), (-0.25, 0.0025, 0.4),
        (0.25, 0.0525, -0.4), (0.25, 0.0025, -0.4), (0.25, 0.0525, 0.4), (0.25, 0.0025, 0.4),
        (0.2, 0.0025, 0.3), (-0.2, 0.0025, 0.3), (-0.2, 0.0025, -0.3), (0.2, 0.0025, -0.3),
    ]
    uvs = [
        (0.913, 0.696), (1.0, 0.435), (0.435, 0.0), (0.87, 0.696),
        (0.957, 0.435), (0.913, 0.0), (1.0, 0.435), (0.435, 0.696),
        (0.87, 0.0), (0.957, 0.435), (0.957, 0.0), (1.0, 0.87),
        (0.0, 0.0), (0.913, 0.0), (0.957, 0.87), (1.0, 0.0),
        (0.957, 0.696), (0.0, 0.696), (0.957, 0.0), (0.913, 0.696),
        (0.826, 0.609), (0.478, 0.609), (0.478, 0.087), (0.826, 0.087),
        (0.435, 0.696), (0.87, 0.696), (0.435, 0.0), (0.87, 0.0),
    ]
    uvIndices = [
        0, 3, 8, 5, 6, 9, 18, 15, 16, 19, 13, 10, 11, 14, 4, 1,
        7, 17, 12, 2, 20, 21, 22, 23, 21, 20, 25, 24, 22, 21, 24, 26,
        23, 22, 26, 27, 20, 23, 27, 25,
    ]
    # fmt: on

    meshPrimName = usdex.core.getValidChildName(parent, meshName)
    if meshPrimName != meshName:
        print(f"Renaming input mesh name <{meshName}> to the valid USD prim name <{meshPrimName}>")

    normalsPrimvarData = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.uniform, normals)
    normalsPrimvarData.index()
    uvsPrimvarData = usdex.core.Vec2fPrimvarData(UsdGeom.Tokens.faceVarying, uvs, uvIndices)
    uvsPrimvarData.index()

    meshPrim = usdex.core.definePolyMesh(
        parent=parent,
        name=meshPrimName,
        faceVertexCounts=faceVertexCounts,
        faceVertexIndices=faceVertexIndices,
        points=points,
        normals=normalsPrimvarData,
        uvs=uvsPrimvarData,
        displayColor=usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, [Gf.Vec3f(0.5, 0.5, 0.5)]),
    )
    if not meshPrim:
        return meshPrim

    usdex.core.setEffectiveDisplayName(meshPrim.GetPrim(), meshName)

    if localPos != Gf.Vec3d(0.0):
        usdex.core.setLocalTransform(
            xformable=meshPrim,
            translation=localPos,
            pivot=Gf.Vec3d(0.0),
            rotation=Gf.Vec3f(0.0),
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
            time=Usd.TimeCode.Default(),
        )

    return meshPrim
