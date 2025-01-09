# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import traceback
from typing import Optional

import sys
sys.path.append("/home/yunliu/.local/lib/python3.10/site-packages")

import vtk
import usdex.core
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, Vt


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
    # Attempt to open the layer first because this doesn't issue a runtime error
    layer = Sdf.Layer.FindOrOpen(identifier)
    stage = None
    try:
        if not layer:
            # Create/overwrite a USD stage, ensuring that key metadata is set
            # NOTE: UsdGeom.GetFallbackUpAxis() is typically set to UsdGeom.Tokens.y
            fileFormatArgs = fileFormatArgs or dict()
            stage = usdex.core.createStage(
                identifier=identifier,
                defaultPrimName=defaultPrimName,
                upAxis=UsdGeom.GetFallbackUpAxis(),
                linearUnits=UsdGeom.LinearUnits.centimeters,
                authoringMetadata=getSamplesAuthoringMetadata(),
                fileFormatArgs=fileFormatArgs,
            )
        else:
            stage = Usd.Stage.Open(identifier)
    except Tf.ErrorException:
        print(traceback.format_exc())

    return stage


def setOmniverseRefinement(prim: Usd.Prim, enabled: bool = True, level: int = 2):
    """Set custom attributes for curved geom prim refinement in NVIDIA Omniverse RTX"""
    attr = prim.CreateAttribute("refinementEnableOverride", Sdf.ValueTypeNames.Bool)
    attr.Set(enabled)
    attr.SetDisplayName("omniRefinementEnableOverride")
    attr = prim.CreateAttribute("refinementLevel", Sdf.ValueTypeNames.Int)
    attr.Set(level)
    attr.SetDisplayName("omniRefinementLevel")


def setExtents(prim: UsdGeom.Boundable):
    """Compute and set the extents on a prim"""
    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(prim, Usd.TimeCode.Default())
    prim.GetExtentAttr().Set(extent)


def createCube(parent: Usd.Prim, name: str = "cube", size: float = 100) -> UsdGeom.Cube:
    """Create a cube prim as a child of the parent prim

    Args:
        parent (Usd.Prim): The parent prim to create the cube under
        name (str): The proposed name of the cube prim
        size (float, optional): The size of the cube. Defaults to 100

    Returns:
        UsdGeom.Cube: The created cube prim
    """
    # Get a valid, unique child prim name under the parent prim
    primNames = usdex.core.getValidChildNames(parent, [name])
    cubePrimPath = parent.GetPath().AppendChild(primNames[0])
    cube = UsdGeom.Cube.Define(parent.GetStage(), cubePrimPath)
    cube.GetSizeAttr().Set(size)
    setExtents(cube)
    return cube


def createCone(
    parent: Usd.Prim,
    name: str = "cone",
    axis: str = UsdGeom.GetFallbackUpAxis(),
    height: float = 100,
    radius: float = 50,
) -> UsdGeom.Cone:
    """Create a UsdGeom.Cone prim with Omniverse refinement and extents

    Args:
        parent (Usd.Prim): The parent prim to create the cone under
        name (str, optional): The proposed name of the cone prim. Defaults to "cone"
        axis (str, optional): The axis along which the cone is aligned. Defaults to UsdGeom.GetFallbackUpAxis(), which is typically UsdGeomTokens->y
        height (float, optional): The height of the cone. Defaults to 100
        radius (float, optional): The radius of the cone. Defaults to 50

    Returns:
        UsdGeom.Cone: The created cone prim
    """
    primNames = usdex.core.getValidChildNames(parent, [name])
    primPath = parent.GetPath().AppendChild(primNames[0])
    cone = UsdGeom.Cone.Define(parent.GetStage(), primPath)
    cone.GetAxisAttr().Set(axis)
    cone.GetHeightAttr().Set(height)
    cone.GetRadiusAttr().Set(radius)
    setOmniverseRefinement(cone.GetPrim())
    setExtents(cone)
    return cone


def createCylinder(
    parent: Usd.Prim,
    name: str = "cylinder",
    axis: str = UsdGeom.GetFallbackUpAxis(),
    height: float = 400,
    radius: float = 50,
) -> UsdGeom.Cylinder:
    """Create a UsdGeom.Cylinder as a child of the parent prim with Omniverse refinement and extents

    Args:
        parent (Usd.Prim): The parent prim to create the cylinder under
        name (str, optional): The proposed name of the cylinder prim. Defaults to "cylinder"
        axis (str, optional): The axis along which the cylinder is aligned. Defaults to UsdGeom.GetFallbackUpAxis(), which is typically UsdGeomTokens->y
        height (float, optional): The height of the cylinder. Defaults to 400
        radius (float, optional): The radius of the cylinder. Defaults to 50

    Returns:
        UsdGeom.Cone: The created cylinder prim
    """
    primNames = usdex.core.getValidChildNames(parent, [name])
    primPath = parent.GetPath().AppendChild(primNames[0])
    cylinder = UsdGeom.Cylinder.Define(parent.GetStage(), primPath)
    cylinder.GetAxisAttr().Set(axis)
    cylinder.GetHeightAttr().Set(height)
    cylinder.GetRadiusAttr().Set(radius)
    setOmniverseRefinement(cylinder.GetPrim())
    setExtents(cylinder)
    return cylinder


def createCubeMesh(parent: str, meshName: str = "cubeMesh", halfHeight: float = 50.0, localPos: Gf.Vec3d = Gf.Vec3d(0.0)) -> UsdGeom.Mesh:
    """
    Creates a cube mesh with the specified half height and local position

    Args:
        parent (str): The parent prim for the new cube mesh
        meshName (str, optional): The name of the mesh. Defaults to "cubeMesh"
        halfHeight (float, optional): The half height of the cube. Defaults to 50.0
        localPos (Gf.Vec3d, optional): The local position of the cube. Defaults to 0,0,0

    Returns:
        UsdGeom.Mesh: The created cube mesh
    """
    # fmt: off
    h = halfHeight
    cubeVertexIndices = [
        0, 1, 2, 1, 3, 2,
        4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11,
        12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19,
        20, 21, 22, 20, 22, 23,
    ]
    cubeVertexCounts = [3] * 12
    cubeNormals = [
        (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
        (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
        (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
        (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
        (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
        (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
    ]
    cubePoints = [
        (h, -h, -h), (-h, -h, -h), (h, h, -h), (-h, h, -h),
        (h, h, h), (-h, h, h), (-h, -h, h), (h, -h, h),
        (h, -h, h), (-h, -h, h), (-h, -h, -h), (h, -h, -h),
        (h, h, h), (h, -h, h), (h, -h, -h), (h, h, -h),
        (-h, h, h), (h, h, h), (h, h, -h), (-h, h, -h),
        (-h, -h, h), (-h, h, h), (-h, h, -h), (-h, -h, -h),
    ]
    cubeUVs = [
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

    # Create the mesh
    normalsPrimvarData = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.vertex, cubeNormals)
    normalsPrimvarData.index()
    uvsPrimvarData = usdex.core.Vec2fPrimvarData(UsdGeom.Tokens.vertex, cubeUVs)
    uvsPrimvarData.index()
    meshPrim = usdex.core.definePolyMesh(
        stage=parent.GetStage(),
        path=meshPrimPath,
        faceVertexCounts=cubeVertexCounts,
        faceVertexIndices=cubeVertexIndices,
        points=cubePoints,
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
            prim=meshPrim.GetPrim(),
            translation=localPos,
            pivot=Gf.Vec3d(0.0),
            rotation=Gf.Vec3f(0.0),
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
            time=Usd.TimeCode.Default(),
        )
    return meshPrim


def convert_to_mesh(
    segmentation_path, label_value=1, smoothing_factor=0.5, reduction_ratio=0.0
):
    """
    Function to perform segmentation-to-mesh conversion and smoothing from NIFTI image
    """
    # Step 1: Load segmentation (binary labelmap, e.g., NRRD file)
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(segmentation_path)
    reader.Update()

    # Step 2: Create Closed Surface Representation using vtkDiscreteFlyingEdges3D
    flying_edges = vtk.vtkDiscreteFlyingEdges3D()
    flying_edges.SetInputConnection(reader.GetOutputPort())
    flying_edges.ComputeGradientsOff()
    flying_edges.ComputeNormalsOff()
    flying_edges.SetValue(0, label_value)
    flying_edges.Update()

    if flying_edges.GetOutput().GetNumberOfPoints() == 0:
        print(f"No points found for label {label_value}. Skipping...")
        return None

    # Step 3: Decimate the mesh
    if reduction_ratio > 0.0:
        decimation_filter = vtk.vtkDecimatePro()
        decimation_filter.SetInputConnection(flying_edges.GetOutputPort())
        decimation_filter.SetFeatureAngle(60)
        decimation_filter.SplittingOff()
        decimation_filter.PreserveTopologyOn()
        decimation_filter.SetMaximumError(1)
        decimation_filter.SetTargetReduction(reduction_ratio)
        decimation_filter.Update()

    # Step 4: Smooth the resulting mesh
    smoothing_filter = vtk.vtkWindowedSincPolyDataFilter()
    numberOfIterations = int(20 + smoothing_factor * 40)
    passBand = pow(10.0, -4.0 * smoothing_factor)
    if reduction_ratio > 0.0:
        smoothing_filter.SetInputConnection(decimation_filter.GetOutputPort())
    else:
        smoothing_filter.SetInputConnection(flying_edges.GetOutputPort())
    smoothing_filter.SetNumberOfIterations(numberOfIterations)
    smoothing_filter.SetPassBand(passBand)
    smoothing_filter.BoundarySmoothingOff()
    smoothing_filter.FeatureEdgeSmoothingOff()
    smoothing_filter.NonManifoldSmoothingOn()
    smoothing_filter.NormalizeCoordinatesOn()
    smoothing_filter.Update()

    # Step 5: Decimate the mesh further
    decimation = vtk.vtkQuadricDecimation()
    decimation.SetInputConnection(smoothing_filter.GetOutputPort())
    decimation.SetTargetReduction(0.9)  # 90% reduction, the same as slicer
    decimation.VolumePreservationOn()
    decimation.Update()

    # Step 6: Generate normals for better shading
    decimatedNormals = vtk.vtkPolyDataNormals()
    decimatedNormals.SetInputConnection(decimation.GetOutputPort())
    decimatedNormals.SplittingOff()
    decimatedNormals.ConsistencyOn()
    decimatedNormals.Update()

    # Step 7: convert to LPS
    ras2lps = vtk.vtkMatrix4x4()
    ras2lps.SetElement(0, 0, -1)
    ras2lps.SetElement(1, 1, -1)
    ras2lpsTransform = vtk.vtkTransform()
    ras2lpsTransform.SetMatrix(ras2lps)
    transformer = vtk.vtkTransformPolyDataFilter()
    transformer.SetTransform(ras2lpsTransform)
    transformer.SetInputConnection(decimatedNormals.GetOutputPort())
    transformer.Update()
    
    return transformer


def createMeshFromVtk(parent, meshName, vtkData, color, translation=Gf.Vec3d(0.0), rotation=Gf.Vec3f(0.0, 0.0, 180.0)):
    meshPrimPath = parent.GetPath().AppendChild(meshName)
    print(f"Creating mesh at path: {meshPrimPath}")
    
    # Create a new USD mesh under the parent
    meshPrim = UsdGeom.Mesh.Define(parent.GetStage(), meshPrimPath)
    
    # Extract points and polygons from the VTK data
    points = vtkData.GetPoints()
    polys = vtkData.GetPolys()
    
    # Convert VTK points to USD points
    usdPoints = []
    for i in range(points.GetNumberOfPoints()):
        p = points.GetPoint(i)
        usdPoints.append(Gf.Vec3f(p[0], p[1], p[2]))
    
    # Convert VTK polygons to USD face vertex indices
    usdFaceVertexIndices = []
    usdFaceVertexCounts = []
    polys.InitTraversal()
    idList = vtk.vtkIdList()
    while polys.GetNextCell(idList):
        usdFaceVertexCounts.append(idList.GetNumberOfIds())
        for j in range(idList.GetNumberOfIds()):
            usdFaceVertexIndices.append(idList.GetId(j))
    
    # Set the points and face vertex indices on the USD mesh
    meshPrim.GetPointsAttr().Set(usdPoints)
    meshPrim.GetFaceVertexIndicesAttr().Set(usdFaceVertexIndices)
    meshPrim.GetFaceVertexCountsAttr().Set(usdFaceVertexCounts)
    
    color = [Gf.Vec3f(color)]
    primvar = meshPrim.GetDisplayColorPrimvar()
    usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, color).setPrimvar(primvar)
    
    # Set initial transformation if localPos != 0,0,0
    if translation != Gf.Vec3d(0.0):
        usdex.core.setLocalTransform(
            prim=meshPrim.GetPrim(),
            translation=translation,
            pivot=Gf.Vec3d(0.0),
            rotation=rotation,
            rotationOrder=usdex.core.RotationOrder.eXyz,
            scale=Gf.Vec3f(1),
            time=Usd.TimeCode.Default(),
        )
    
    return meshPrim
