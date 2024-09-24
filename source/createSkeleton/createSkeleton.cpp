// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/MeshAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/usd/usd/relationship.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdSkel/animQuery.h>
#include <pxr/usd/usdSkel/animation.h>
#include <pxr/usd/usdSkel/bindingAPI.h>
#include <pxr/usd/usdSkel/cache.h>
#include <pxr/usd/usdSkel/root.h>
#include <pxr/usd/usdSkel/skeleton.h>
#include <pxr/usd/usdSkel/utils.h>

#include <iostream>


namespace
{
static constexpr const char g_animName[] = "anim";
static constexpr const char g_skelName[] = "skel";
static constexpr const char g_skinnedMeshName[] = "skinnedMesh";
static const double g_boneSize = 100.0;
static const double g_timeCodesPerSecond = 24;
static const double g_endTimeCode = 48;
} // namespace


//! Create an example animation for the example skeleton
//!
//! @param skeleton The skeleton prim
//! @param animPrimPath The path to the animation prim to be created
//! @param elbowMaxAngle The max angle for the elbow joint in the animation (on the joint's X axis)
//! @param wristMaxAngle The max angle for the wrist joint in the animation (on the joint's Z axis)
//! @return The created UsdSkelAnimation prim
pxr::UsdSkelAnimation createAndBindAnimForSkel(
    pxr::UsdSkelSkeleton& skeleton,
    const pxr::SdfPath& animPrimPath,
    double elbowMaxAngle,
    double wristMaxAngle
)
{
    pxr::UsdSkelAnimation anim = pxr::UsdSkelAnimation::Define(skeleton.GetPrim().GetStage(), animPrimPath);

    // Create the joint array (rotating the elbow and wrist)
    pxr::VtTokenArray jointTokens;
    skeleton.GetJointsAttr().Get(&jointTokens);
    pxr::VtTokenArray animJointTokens = {
        jointTokens[1], // elbow
        jointTokens[2] // wrist
    };
    anim.CreateJointsAttr(pxr::VtValue(animJointTokens));

    // Set constant relative translation and scale attributes
    pxr::VtVec3fArray translations = {
        pxr::GfVec3f(0, 0, g_boneSize), // elbow
        pxr::GfVec3f(0, 0, g_boneSize) // wrist
    };

    // Rotate the elbow
    std::vector<pxr::GfRotation> elbowRots = { pxr::GfRotation(pxr::GfVec3d(1, 0, 0), 0),
                                               pxr::GfRotation(pxr::GfVec3d(1, 0, 0), elbowMaxAngle),
                                               pxr::GfRotation(pxr::GfVec3d(1, 0, 0), 0) };

    // Rotate the wrist
    std::vector<pxr::GfRotation> wristRots = { pxr::GfRotation(pxr::GfVec3d(1, 0, 0), 0),
                                               pxr::GfRotation(pxr::GfVec3d(0, 0, 1), wristMaxAngle),
                                               pxr::GfRotation(pxr::GfVec3d(1, 0, 0), 0) };

    // Time samples over 2 seconds (g_endTimeCode frames at timeCodesPerSecond FPS)
    std::vector<pxr::UsdTimeCode> timeCodes = { pxr::UsdTimeCode(0), pxr::UsdTimeCode(g_endTimeCode * 0.5), pxr::UsdTimeCode(g_endTimeCode) };

    // As indicated in https://openusd.org/dev/api/_usd_skel__a_p_i__intro.html#UsdSkel_API_WritingSkels one may use
    // pxr::UsdSkelAnimation::SetTransforms() rather than setting the vectorized arrays of translation, rotation, and scale separately.
    // In a DCC app there may be a matrix for every joint every frame.  For the sake of demonstration
    // we've used the above translations, scales, and rotations
    for (size_t i = 0; i < timeCodes.size(); ++i)
    {
        pxr::VtMatrix4dArray mat4ds(2);
        pxr::UsdSkelMakeTransform<pxr::GfMatrix4d>(translations[0], elbowRots[i], pxr::GfVec3h(1), &mat4ds[0]);
        pxr::UsdSkelMakeTransform<pxr::GfMatrix4d>(translations[1], wristRots[i], pxr::GfVec3h(1), &mat4ds[1]);
        anim.SetTransforms(mat4ds, timeCodes[i]);
    }

    pxr::UsdSkelBindingAPI skelBinding = pxr::UsdSkelBindingAPI::Apply(skeleton.GetPrim());
    skelBinding.CreateAnimationSourceRel().SetTargets(pxr::SdfPathVector({ animPrimPath }));

    return anim;
}


//! Create a simple skinned skel mesh quad with an animation
//!
//! This function creates a SkelRoot as the parent prim for a Skeleton, Skeleton Animation, and Mesh.  The Mesh is
//! skinned to the skeleton, and the skeleton sets the animation as its animation source.  Extents are also computed and authored
//! for the various boundable (skel root, skeleton) and point-based (mesh) prims.
//!
//! This function will also modify the stage metadata to set the frame rate to g_timeCodesPerSecond and the end time code to g_endTimeCode.
//!
//! Learn more from the OpenUSD docs: https://openusd.org/dev/api/_usd_skel__schema_overview.html#UsdSkel_SchemaOverview_DefiningSkeletons
//!
//! @param parent The parent prim for the SkelRoot prim where the skeleton, mesh, and animation are created
//! @param skelRootName The name of the SkelRoot prim
//! @param initialTranslation The initial world translation for the SkelRoot
//! @return The created UsdSkelRoot prim
pxr::UsdSkelRoot createSkelMesh(
    pxr::UsdPrim parent,
    const char* skelRootName = "skelRootGroup",
    const pxr::GfVec3d& initialTranslation = pxr::GfVec3d(0)
)
{
    pxr::UsdStageRefPtr stage = parent.GetStage();

    // Create the skelroot group under the parent prim
    pxr::TfTokenVector skelRootPrimNames = usdex::core::getValidChildNames(parent, std::vector<std::string>{ skelRootName });
    const pxr::SdfPath skelRootPrimPath = parent.GetPath().AppendChild(skelRootPrimNames[0]);

    //////////////
    // SkelRoot //
    //////////////
    pxr::UsdSkelRoot skelRoot = pxr::UsdSkelRoot::Define(stage, skelRootPrimPath);

    // A UsdSkel should be moved around at or above its SkelRoot, push it away from the center of the stage
    usdex::core::setLocalTransform(
        skelRoot.GetPrim(),
        initialTranslation, // translation
        pxr::GfVec3d(0), // pivot
        pxr::GfVec3f(0), // rotation
        usdex::core::RotationOrder::eXyz,
        pxr::GfVec3f(1) // scale
    );

    // Get valid child prim names for the skeleton, animation, and mesh
    std::vector<std::string> skelChildNames({ g_skelName, g_animName, g_skinnedMeshName });
    pxr::TfTokenVector skelChildPrimNames = usdex::core::getValidChildNames(skelRoot.GetPrim(), skelChildNames);


    //////////////
    // Skeleton //
    //////////////
    const pxr::SdfPath skelPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[0]);
    pxr::UsdSkelSkeleton skeleton = pxr::UsdSkelSkeleton::Define(stage, skelPrimPath);

    // joint paths
    pxr::VtTokenArray jointTokens = { pxr::TfToken("Shoulder"), pxr::TfToken("Shoulder/Elbow"), pxr::TfToken("Shoulder/Elbow/Wrist") };

    pxr::UsdSkelTopology topo(jointTokens);
    std::string reason;
    if (!topo.Validate(&reason))
    {
        std::cout << "Invalid skeleton topology: " << reason.c_str() << std::endl;
        ;
        return pxr::UsdSkelRoot();
    }
    skeleton.GetJointsAttr().Set(jointTokens);

    // bind transforms - provide the world space transform of each joint at bind time
    pxr::VtMatrix4dArray bindTransforms({ pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, -g_boneSize, 1),
                                          pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
                                          pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1) });
    skeleton.GetBindTransformsAttr().Set(bindTransforms);

    // rest transforms - provides local space rest transforms of each joint
    // (serve as a fallback values for joints not overridden by an animation)
    pxr::VtMatrix4dArray restTransforms({ pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
                                          pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1),
                                          pxr::GfMatrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, g_boneSize, 1) });
    skeleton.GetRestTransformsAttr().Set(restTransforms);

    ///////////////
    // Skel Anim //
    ///////////////
    const pxr::SdfPath animPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[1]);

    // Create anim with a max elbow angle of -45 and a max wrist angle of 20
    // This function also binds ths animation to the skeleton
    pxr::UsdSkelAnimation animPrim = createAndBindAnimForSkel(skeleton, animPrimPath, -45, 20);

    // Set the stage time-codes-per-second and end-time-code
    // NOTE: This is a stage-global operation, placed here for necessity.
    //       Ideally the end time code might take other animations in the stage into consideration.
    stage->SetTimeCodesPerSecond(g_timeCodesPerSecond);
    stage->SetStartTimeCode(0);
    if (stage->GetEndTimeCode() < g_endTimeCode)
    {
        stage->SetEndTimeCode(g_endTimeCode);
    }

    //////////////////
    // Skinned Mesh //
    //////////////////
    const pxr::SdfPath meshPrimPath = skelRoot.GetPrim().GetPath().AppendChild(skelChildPrimNames[2]);

    /***************
       point/vertex and joint map:

       2---j2---3
       |   |    |
       1---j1---4
       |   |    |
       0---j0---5
   ****************/
    pxr::VtVec3fArray points = {
        pxr::GfVec3f(-g_boneSize, 0.0, -g_boneSize), pxr::GfVec3f(-g_boneSize, 0.0, 0.0), pxr::GfVec3f(-g_boneSize, 0.0, g_boneSize),
        pxr::GfVec3f(g_boneSize, 0.0, g_boneSize),   pxr::GfVec3f(g_boneSize, 0.0, 0.0),  pxr::GfVec3f(g_boneSize, 0.0, -g_boneSize),
    };

    // Indices for each quad
    pxr::VtIntArray faceVertexIndices = { 0, 1, 4, 5, 1, 2, 3, 4 };

    // Face vertex count
    pxr::VtIntArray faceVertexCounts = { 4, 4 };

    // Vertex normals
    pxr::VtVec3fArray normals = { pxr::GfVec3f(0.0, 1.0, 0.0) };
    pxr::VtIntArray normalIndices = { 0, 0, 0, 0, 0, 0 };

    pxr::UsdGeomMesh mesh = usdex::core::definePolyMesh(
        stage,
        meshPrimPath,
        faceVertexCounts,
        faceVertexIndices,
        points,
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->vertex, normals, normalIndices), /* normals */
        std::nullopt, /* no UVs */
        usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, { { 1.0f, 0.5f, 0.0f } }) /* displayColor */
    );

    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Apply the SkelBindingAPI to the mesh                                                                                     //
    // Rigid deformations docs: https://openusd.org/release/api/_usd_skel__schemas.html#UsdSkel_BindingAPI_RigidDeformations    //
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    pxr::UsdSkelBindingAPI binding = pxr::UsdSkelBindingAPI::Apply(mesh.GetPrim());
    binding.CreateSkeletonRel().SetTargets(pxr::SdfPathVector({ skelPrimPath }));

    bool rigidDeformation = false;
    // Joint indices - vert to joint indices mapping
    pxr::VtIntArray jointIndices = { 0, 1, 2, 2, 1, 0 };
    binding.CreateJointIndicesPrimvar(rigidDeformation).Set(pxr::VtValue(jointIndices));

    // Joint weights - vert to joint weight mapping
    pxr::VtFloatArray jointWeights = { 1, 1, 1, 1, 1, 1 };
    binding.CreateJointWeightsPrimvar(rigidDeformation).Set(pxr::VtValue(jointWeights));

    // GeomBindTransform - For skinning to apply correctly set the bind-time world space transforms of the prim
    binding.CreateGeomBindTransformAttr().Set(pxr::VtValue(pxr::GfMatrix4d(1)));

    ///////////////////////////////////////////////////
    // Compute extents for the SkelRoot and Skeleton //
    ///////////////////////////////////////////////////
    pxr::VtVec3fArray extent;
    std::vector<double> timesamples;

    pxr::UsdGeomBoundable::ComputeExtentFromPlugins(skelRoot, pxr::UsdTimeCode::Default(), &extent);
    skelRoot.GetExtentAttr().Set(pxr::VtValue(extent), pxr::UsdTimeCode::Default());

    pxr::UsdGeomBoundable::ComputeExtentFromPlugins(skeleton, pxr::UsdTimeCode::Default(), &extent);
    skeleton.GetExtentAttr().Set(pxr::VtValue(extent), pxr::UsdTimeCode::Default());

    pxr::UsdSkelCache skelCache;
    pxr::UsdSkelAnimQuery animQuery = skelCache.GetAnimQuery(animPrim);
    animQuery.GetJointTransformTimeSamples(&timesamples);
    for (double time : timesamples)
    {
        pxr::UsdGeomBoundable::ComputeExtentFromPlugins(skelRoot, pxr::UsdTimeCode(time), &extent);
        skelRoot.GetExtentAttr().Set(pxr::VtValue(extent), pxr::UsdTimeCode(time));

        pxr::UsdGeomBoundable::ComputeExtentFromPlugins(skeleton, pxr::UsdTimeCode(time), &extent);
        skeleton.GetExtentAttr().Set(pxr::VtValue(extent), pxr::UsdTimeCode(time));
    }

    return skelRoot;
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createSkeleton", "Creates a skeleton using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    pxr::UsdSkelRoot skelRoot = createSkelMesh(stage->GetDefaultPrim(), "skelRootGroup", pxr::GfVec3d(-300, 0, 0));
    if (!skelRoot)
    {
        std::cout << "Error creating skeletal mesh group, exiting" << std::endl;
        return -1;
    }

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
