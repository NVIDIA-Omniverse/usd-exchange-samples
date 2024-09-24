# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from pxr import Gf, Usd, UsdGeom, UsdSkel, Vt

g_animName = "anim"
g_skelName = "skel"
g_skinnedMeshName = "skinnedMesh"
g_boneSize = 100.0
g_timeCodesPerSecond = 24
g_endTimeCode = 48


def createAndBindAnimForSkel(skeleton: UsdSkel.Skeleton, animPrimPath: str, elbowMaxAngle: float, wristMaxAngle: float) -> UsdSkel.Animation:
    """
    Create an example animation for the example skeleton

    Args:
        skeleton: The skeleton prim
        animPrimPath: The path to the animation prim to be created
        elbowMaxAngle: The max angle for the elbow joint in the animation (on the joint's X axis)
        wristMaxAngle: The max angle for the wrist joint in the animation (on the joint's Z axis)

    Returns:
        The created UsdSkel.Animation prim
    """
    anim = UsdSkel.Animation.Define(skeleton.GetPrim().GetStage(), animPrimPath)

    # Create the joint array (rotating the elbow and wrist)
    jointTokens = skeleton.GetJointsAttr().Get()
    animJointTokens = [
        jointTokens[1],  # elbow
        jointTokens[2],  # wrist
    ]
    anim.CreateJointsAttr(animJointTokens)

    # Set constant relative translation and scale attributes
    translations = [
        Gf.Vec3f(0, 0, g_boneSize),  # elbow
        Gf.Vec3f(0, 0, g_boneSize),  # wrist
    ]

    # Rotate the elbow
    elbowRots = [
        Gf.Rotation(Gf.Vec3d(1, 0, 0), 0),
        Gf.Rotation(Gf.Vec3d(1, 0, 0), elbowMaxAngle),
        Gf.Rotation(Gf.Vec3d(1, 0, 0), 0),
    ]

    # Rotate the wrist
    wristRots = [
        Gf.Rotation(Gf.Vec3d(1, 0, 0), 0),
        Gf.Rotation(Gf.Vec3d(0, 0, 1), wristMaxAngle),
        Gf.Rotation(Gf.Vec3d(1, 0, 0), 0),
    ]

    # Time samples over 2 seconds (g_endTimeCode frames at timeCodesPerSecond FPS)
    timeCodes = [
        Usd.TimeCode(0),
        Usd.TimeCode(g_endTimeCode * 0.5),
        Usd.TimeCode(g_endTimeCode),
    ]

    # As indicated in https:#openusd.org/dev/api/_usd_skel__a_p_i__intro.html#UsdSkel_API_WritingSkels one may use
    # UsdSkelAnimation.SetTransforms() rather than setting the vectorized arrays of translation, rotation, and scale separately.
    # In a DCC app there may be a matrix for every joint every frame.  For the sake of demonstration
    # we've used the above translations, scales, and rotations
    for i, timeCode in enumerate(timeCodes):
        mat0 = UsdSkel.MakeTransform(translations[0], Gf.Quatf(elbowRots[i].GetQuat()), Gf.Vec3h(1))
        mat1 = UsdSkel.MakeTransform(translations[1], Gf.Quatf(wristRots[i].GetQuat()), Gf.Vec3h(1))
        anim.SetTransforms([mat0, mat1], timeCode)

    skelBinding = UsdSkel.BindingAPI.Apply(skeleton.GetPrim())
    skelBinding.CreateAnimationSourceRel().SetTargets([animPrimPath])
    return anim


def createSkelMesh(parent: Usd.Prim, skelRootName: str = "skelRootGroup", initialTranslation: Gf.Vec3d = Gf.Vec3d(0)) -> UsdSkel.Root:
    """
    Create a simple skinned skel mesh quad with an animation

    This function creates a SkelRoot as the parent prim for a Skeleton, Skeleton Animation, and Mesh.  The Mesh is
    skinned to the skeleton, and the skeleton sets the animation as its animation source.  Extents are also computed and authored
    for the various boundable (skel root, skeleton) and point-based (mesh) prims.

    This function will also modify the stage metadata to set the frame rate to g_timeCodesPerSecond and the end time code to g_endTimeCode.

    Learn more from the OpenUSD docs: https://openusd.org/dev/api/_usd_skel__schema_overview.html#UsdSkel_SchemaOverview_DefiningSkeletons

    Args:
        parent The parent prim for the SkelRoot prim where the skeleton, mesh, and animation are created
        skelRootName The name of the SkelRoot prim
        initialTranslation The initial world translation for the SkelRoot

    Returns:
        The created UsdSkel.Root prim
    """
    stage = parent.GetStage()

    # Create the skelroot group under the parent prim
    skelRootPrimNames = usdex.core.getValidChildNames(parent, [skelRootName])
    skelRootPrimPath = parent.GetPath().AppendChild(skelRootPrimNames[0])

    ############
    # SkelRoot #
    ############
    skelRoot = UsdSkel.Root.Define(stage, skelRootPrimPath)

    # A UsdSkel should be moved around at or above its SkelRoot, push it away from the center of the stage
    usdex.core.setLocalTransform(
        prim=skelRoot.GetPrim(),
        translation=initialTranslation,
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0.0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1),
    )

    # Get valid child prim names for the skeleton, animation, and mesh
    skelChildNames = [g_skelName, g_animName, g_skinnedMeshName]
    skelChildPrimNames = usdex.core.getValidChildNames(parent, skelChildNames)

    ############
    # Skeleton #
    ############
    skelPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[0])
    skeleton = UsdSkel.Skeleton.Define(stage, skelPrimPath)

    # joint paths
    jointTokens = ["Shoulder", "Shoulder/Elbow", "Shoulder/Elbow/Wrist"]

    topo = UsdSkel.Topology(jointTokens)
    valid, reason = topo.Validate()
    if not valid:
        print(f"Invalid skeleton topology: %s", reason)
        return UsdSkel.Root()

    skeleton.GetJointsAttr().Set(jointTokens)

    # bind transforms - provide the world space transform of each joint at bind time
    bindTransforms = Vt.Matrix4dArray(
        [
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, -g_boneSize, 1),
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1),
        ]
    )
    skeleton.GetBindTransformsAttr().Set(bindTransforms)

    # rest transforms - provides local space rest transforms of each joint
    # (serve as a fallback values for joints not overridden by an animation)
    restTransforms = Vt.Matrix4dArray(
        [
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1),
            Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1),
        ]
    )
    skeleton.GetRestTransformsAttr().Set(restTransforms)

    #############
    # Skel Anim #
    #############
    animPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[1])

    # Create anim with a max elbow angle of -45 and a max wrist angle of 20
    # This function also binds ths animation to the skeleton
    animPrim = createAndBindAnimForSkel(skeleton, animPrimPath, -45, 20)

    # Set the stage time-codes-per-second and end-time-code
    # NOTE: This is a stage-global operation, placed here for necessity.
    #       Ideally the end time code might take other animations in the stage into consideration.
    stage.SetTimeCodesPerSecond(g_timeCodesPerSecond)
    stage.SetStartTimeCode(0)
    if stage.GetEndTimeCode() < g_endTimeCode:
        stage.SetEndTimeCode(g_endTimeCode)

    ################
    # Skinned Mesh #
    ################
    meshPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[2])

    ##############################
    #  point/vertex and joint map:
    #
    #  2---j2---3
    #  |   |    |
    #  1---j1---4
    #  |   |    |
    #  0---j0---5
    ##############################
    points = [
        (-g_boneSize, 0.0, -g_boneSize),
        (-g_boneSize, 0.0, 0.0),
        (-g_boneSize, 0.0, g_boneSize),
        (g_boneSize, 0.0, g_boneSize),
        (g_boneSize, 0.0, 0.0),
        (g_boneSize, 0.0, -g_boneSize),
    ]

    # Indices for each quad
    faceVertexIndices = [0, 1, 4, 5, 1, 2, 3, 4]

    # Face vertex count
    faceVertexCounts = [4, 4]

    # Vertex normals
    normals = [(0.0, 1.0, 0.0)]
    normalIndices = [0, 0, 0, 0, 0, 0]
    normalsPrimvarData = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.vertex, normals, normalIndices)

    mesh = usdex.core.definePolyMesh(
        stage=stage,
        path=meshPrimPath,
        faceVertexCounts=faceVertexCounts,
        faceVertexIndices=faceVertexIndices,
        points=points,
        normals=normalsPrimvarData,
        displayColor=usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, [(1, 0.5, 0)]),
    )

    #########################################################################################################################
    # Apply the SkelBindingAPI to the mesh                                                                                  #
    # Rigid deformations docs: https://openusd.org/release/api/_usd_skel__schemas.html#UsdSkel_BindingAPI_RigidDeformations #
    #########################################################################################################################
    binding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
    binding.CreateSkeletonRel().SetTargets([skelPrimPath])

    rigidDeformation = False
    # Joint indices - vert to joint indices mapping
    jointIndices = [0, 1, 2, 2, 1, 0]
    binding.CreateJointIndicesPrimvar(rigidDeformation).Set(jointIndices)

    # Joint weights - vert to joint weight mapping
    jointWeights = [1, 1, 1, 1, 1, 1]
    binding.CreateJointWeightsPrimvar(rigidDeformation).Set(jointWeights)

    # GeomBindTransform - For skinning to apply correctly set the bind-time world space transforms of the prim
    binding.CreateGeomBindTransformAttr().Set(Gf.Matrix4d(1))

    #################################################
    # Compute extents for the SkelRoot and Skeleton #
    #################################################
    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(skelRoot, Usd.TimeCode.Default())
    skelRoot.GetExtentAttr().Set(extent, Usd.TimeCode.Default())

    extent = UsdGeom.Boundable.ComputeExtentFromPlugins(skeleton, Usd.TimeCode.Default())
    skeleton.GetExtentAttr().Set(extent, Usd.TimeCode.Default())

    skelCache = UsdSkel.Cache()
    animQuery = skelCache.GetAnimQuery(animPrim)
    timesamples = animQuery.GetJointTransformTimeSamples()
    for time in timesamples:
        extent = UsdGeom.Boundable.ComputeExtentFromPlugins(skelRoot, Usd.TimeCode(time))
        skelRoot.GetExtentAttr().Set(extent, Usd.TimeCode(time))

        extent = UsdGeom.Boundable.ComputeExtentFromPlugins(skeleton, Usd.TimeCode(time))
        skeleton.GetExtentAttr().Set(extent, Usd.TimeCode(time))

    return skelRoot


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    skelRoot = createSkelMesh(stage.GetDefaultPrim(), "skelRootGroup", (-300, 0, 0))
    if not skelRoot:
        print("Error creating skeletal mesh group, exiting")
        sys.exit(-1)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a skeleton using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
