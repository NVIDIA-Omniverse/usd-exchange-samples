// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/AssetStructure.h>
#include <usdex/core/Core.h>
#include <usdex/core/PhysicsJointAlgo.h>
#include <usdex/core/PhysicsMaterialAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/usd/usd/primRange.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/capsule.h>
#include <pxr/usd/usdGeom/cube.h>
#include <pxr/usd/usdGeom/plane.h>
#include <pxr/usd/usdGeom/scope.h>
#include <pxr/usd/usdGeom/sphere.h>
#include <pxr/usd/usdGeom/tokens.h>
#include <pxr/usd/usdGeom/xformable.h>
#include <pxr/usd/usdPhysics/collisionAPI.h>
#include <pxr/usd/usdPhysics/rigidBodyAPI.h>
#include <pxr/usd/usdPhysics/scene.h>
#include <pxr/usd/usdShade/material.h>

#include <iostream>
#include <vector>

//! Create a physics scene.
//!
//! @param stage Target stage
void createPhysicsScene(pxr::UsdStageRefPtr stage)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Check if the physics scene already exists, we only want one per stage.
    for (const auto& prim : pxr::UsdPrimRange(defaultPrim))
    {
        if (prim.IsA<pxr::UsdPhysicsScene>())
        {
            return;
        }
    }

    // Create physics scene, note that we don't have to specify gravity because
    // the default value is derived from the stage's upAxis and linear scale.
    // In this case the gravity would be (0.0, -981.0, 0.0) since the stage has a
    // Y upAxis with a centimeter linear scale.
    const auto physicsSceneName = usdex::core::getValidChildName(defaultPrim, "PhysicsScene");
    const pxr::SdfPath scenePath = defaultPrim.GetPath().AppendChild(physicsSceneName);
    pxr::UsdPhysicsScene::Define(stage, scenePath);
}

//! Create a ground plane with collision assigned.
//!
//! @param stage A valid stage to create the ground plane in
//!
//! @returns True if the ground plane was created successfully, false otherwise
bool createGroundWithCollision(pxr::UsdStageRefPtr stage)
{
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Check if the plane already exists, we only want one per stage.
    for (const auto& prim : pxr::UsdPrimRange(defaultPrim))
    {
        if (prim.IsA<pxr::UsdGeomPlane>())
        {
            return true;
        }
    }

    const auto groundName = usdex::core::getValidChildName(defaultPrim, "ground");
    pxr::SdfPath groundPath = defaultPrim.GetPath().AppendChild(groundName);
    pxr::UsdGeomPlane plane = pxr::UsdGeomPlane::Define(stage, groundPath);
    if (!plane)
    {
        return false;
    }

    plane.GetAxisAttr().Set(pxr::UsdGeomGetStageUpAxis(stage));

    // Set collider.
    pxr::UsdPhysicsCollisionAPI::Apply(plane.GetPrim());

    // Set transform.
    const pxr::GfVec3d position(0, -50, 0);
    const pxr::GfVec3d pivot(0);
    const pxr::GfVec3f rotation(0, 0, 0);
    const pxr::GfVec3f scale(1, 1, 1);
    usdex::core::setLocalTransform(plane, position, pivot, rotation, usdex::core::RotationOrder::eXyz, scale);

    return true;
}

//! Create simple rigid bodies and collisions.
//!
//! @param stage Target stage
void simpleRigidBodiesAndCollisions(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "SimpleRigidBodies");
    pxr::UsdGeomXform simpleXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    // Create sphere with rigid body and collision.
    {
        const pxr::GfVec3f displayColor(1, 0, 0);
        const pxr::GfVec3d position(0, 200, 0);
        const pxr::GfVec3f rotation(0);
        const pxr::GfVec3f scale(1);
        pxr::UsdGeomSphere sphere = samples::createSphere(simpleXform.GetPrim(), "sphere", 30.0f, position, rotation, scale, displayColor);

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(sphere.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(sphere.GetPrim());
    }

    // Create cube with rigid body and collision.
    {
        const pxr::GfVec3f displayColor(0, 1, 0);
        const pxr::GfVec3d position(120, 250, 0);
        const pxr::GfVec3f rotation(50, 45, 0);
        const pxr::GfVec3f scale(1);
        pxr::UsdGeomCube cube = samples::createCube(simpleXform.GetPrim(), "cube", 50.0f, position, rotation, scale, displayColor);

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(cube.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(cube.GetPrim());
    }
}

//! Create simple physics fixed joints.
//!
//! @param stage Target stage
//! @param centerPos Center position of the base xform
//! @param capsuleCount Number of capsules
void simplePhysicsFixedJoints(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos, const int capsuleCount = 3)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "SimpleFixedJoints");
    pxr::UsdGeomXform baseXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    // Create an Xform to place the joints.
    const auto jointsName = usdex::core::getValidChildName(baseXform.GetPrim(), "joints");
    pxr::UsdGeomXform jointsXform = usdex::core::defineXform(baseXform.GetPrim(), jointsName.GetString());

    // Create a vector of capsule names
    const std::vector<std::string> srcCapsuleNames(capsuleCount, "capsule");
    const auto capsuleNames = usdex::core::getValidChildNames(baseXform.GetPrim(), srcCapsuleNames);

    // Create capsules with rigid body and collision.
    const float capsuleWidth = 80.0f;
    const float capsuleRadius = 10.0f;
    const float capsuleMargin = 2.0f;
    const float capsuleLengthX = capsuleWidth + capsuleRadius * 2.0f + capsuleMargin;
    double px = 0.0;
    const double py = 200.0;
    double pz = 0.0;

    std::vector<pxr::UsdGeomXformable> capsules;
    for (int i = 0; i < capsuleCount; i++, px += capsuleLengthX)
    {
        const pxr::GfVec3f displayColor = (i == 0) ? pxr::GfVec3f(1, 0, 0) : pxr::GfVec3f(0, 1, 0);
        const pxr::GfVec3d position(px, py, pz);
        const pxr::GfVec3f rotation(0.0f, 0.0f, 0.0f);
        const pxr::GfVec3f scale(1);
        const std::string name = capsuleNames[i].GetString();
        pxr::UsdGeomCapsule capsule = samples::createCapsule(
            baseXform.GetPrim(),
            name,
            pxr::UsdGeomTokens->x,
            capsuleWidth,
            capsuleRadius,
            position,
            rotation,
            scale,
            displayColor
        );

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(capsule.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(capsule.GetPrim());

        capsules.push_back(capsule);
    }

    // Connect the root and the first capsule with a FixedJoint to fix them in place.
    {
        pxr::UsdPrim body0 = baseXform.GetPrim();
        pxr::UsdPrim body1 = capsules[0].GetPrim();

        const std::string name = "FixedJoint_root";

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsFixedJoint(
            jointsXform.GetPrim(), // Parent prim.
            name, // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame // Joint frame.
        );
    }

    // Create a vector of joint names
    const std::vector<std::string> srcJointNames(capsuleCount, "FixedJoint");
    const auto jointNames = usdex::core::getValidChildNames(jointsXform.GetPrim(), srcJointNames);

    // Connect two capsules with physics joints.
    for (int i = 1; i < capsuleCount; i++)
    {
        const std::string name = jointNames[i].GetString();

        // The two prims to be connected.
        pxr::UsdPrim body0 = capsules[i - 1].GetPrim();
        pxr::UsdPrim body1 = capsules[i].GetPrim();

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsFixedJoint(
            jointsXform.GetPrim(), // Parent prim.
            name, // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame // Joint frame.
        );
    }
}

//! Create simple physics revolute joints.
//!
//! @param stage Target stage
//! @param centerPos Center position of the base xform
//! @param capsuleCount Number of capsules
void simplePhysicsRevoluteJoints(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos, const int capsuleCount = 3)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "SimpleRevoluteJoints");
    pxr::UsdGeomXform baseXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    // Create an Xform to place the joints.
    const auto jointsName = usdex::core::getValidChildName(baseXform.GetPrim(), "joints");
    pxr::UsdGeomXform jointsXform = usdex::core::defineXform(baseXform.GetPrim(), jointsName.GetString());

    // Create a vector of capsule names
    const std::vector<std::string> srcCapsuleNames(capsuleCount, "capsule");
    const auto capsuleNames = usdex::core::getValidChildNames(baseXform.GetPrim(), srcCapsuleNames);

    // Create capsules with rigid body and collision.
    const float capsuleWidth = 80.0f;
    const float capsuleRadius = 10.0f;
    const float capsuleMargin = 2.0f;
    const float capsuleLengthX = capsuleWidth + capsuleRadius * 2.0f + capsuleMargin;
    double px = 0.0;
    const double py = 200.0;
    double pz = 0.0;

    std::vector<pxr::UsdGeomCapsule> capsules;
    for (int i = 0; i < capsuleCount; i++, px += capsuleLengthX)
    {
        const pxr::GfVec3f displayColor = (i == 0) ? pxr::GfVec3f(1, 0, 0) : pxr::GfVec3f(0, 1, 0);
        const pxr::GfVec3d position(px, py, pz);
        const pxr::GfVec3f rotation(0.0f, 0.0f, 0.0f);
        const pxr::GfVec3f scale(1);
        const std::string name = capsuleNames[i].GetString();
        pxr::UsdGeomCapsule capsule = samples::createCapsule(
            baseXform.GetPrim(),
            name,
            pxr::UsdGeomTokens->x,
            capsuleWidth,
            capsuleRadius,
            position,
            rotation,
            scale,
            displayColor
        );

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(capsule.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(capsule.GetPrim());

        capsules.push_back(capsule);
    }

    // Connect the root and the first capsule with a FixedJoint to fix them in place.
    {
        pxr::UsdPrim body0 = baseXform.GetPrim();
        pxr::UsdPrim body1 = capsules[0].GetPrim();

        const auto fixedJointName = usdex::core::getValidChildName(jointsXform.GetPrim(), "FixedJoint_root");

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsFixedJoint(
            jointsXform.GetPrim(), // Parent prim.
            fixedJointName.GetString(), // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame // Joint frame.
        );
    }

    // Create a vector of joint names
    const std::vector<std::string> srcJointNames(capsuleCount, "RevoluteJoint");
    const auto jointNames = usdex::core::getValidChildNames(jointsXform.GetPrim(), srcJointNames);

    // Connect two capsules with physics joints.
    // The rotation of a RevoluteJoint is primarily about the local Z axis and limits are set in degrees.
    const float lowerLimit = -45.0f;
    const float upperLimit = 20.0f;
    const pxr::GfVec3f axis(0, 0, 1);
    for (int i = 1; i < capsuleCount; i++)
    {
        const std::string name = jointNames[i].GetString();

        // The two prims to be connected.
        pxr::UsdPrim body0 = capsules[i - 1].GetPrim();
        pxr::UsdPrim body1 = capsules[i].GetPrim();

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsRevoluteJoint(
            jointsXform.GetPrim(), // Parent prim.
            name, // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame, // Joint frame.
            axis, // Axis.
            lowerLimit, // Lower limit.
            upperLimit // Upper limit.
        );
    }
}

//! Create simple physics prismatic joints.
//!
//! @param stage Target stage
//! @param centerPos Center position of the base xform
//! @param capsuleCount Number of capsules
void simplePhysicsPrismaticJoints(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos, const int capsuleCount = 3)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "SimplePrismaticJoints");
    pxr::UsdGeomXform baseXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    // Create an Xform to place the joints.
    const auto jointsName = usdex::core::getValidChildName(baseXform.GetPrim(), "joints");
    pxr::UsdGeomXform jointsXform = usdex::core::defineXform(baseXform.GetPrim(), jointsName.GetString());

    // Create capsules with rigid body and collision.
    const float capsuleWidth = 80.0f;
    const float capsuleRadius = 10.0f;
    const float capsuleMargin = 2.0f;
    const float capsuleLengthX = capsuleWidth + capsuleRadius * 2.0f + capsuleMargin;
    double px = 0.0;
    const double py = 200.0;
    double pz = 0.0;

    // Xform tilted slightly downwards.
    pxr::GfTransform tiltTransform;
    tiltTransform.SetTranslation(pxr::GfVec3d(-(capsuleLengthX * 0.5), 0, 0));
    tiltTransform.SetRotation(pxr::GfRotation(pxr::GfVec3d(0, 0, 1), -15.0f));
    const auto tiltName = usdex::core::getValidChildName(baseXform.GetPrim(), "tilt");
    pxr::UsdGeomXform tiltXform = usdex::core::defineXform(baseXform.GetPrim(), tiltName.GetString(), tiltTransform);

    // Create a vector of capsule names
    const std::vector<std::string> srcCapsuleNames(capsuleCount, "capsule");
    const auto capsuleNames = usdex::core::getValidChildNames(tiltXform.GetPrim(), srcCapsuleNames);

    std::vector<pxr::UsdGeomXformable> capsules;
    for (int i = 0; i < capsuleCount; i++, px += capsuleLengthX)
    {
        const pxr::GfVec3f displayColor = (i == 0) ? pxr::GfVec3f(1, 0, 0) : pxr::GfVec3f(0, 1, 0);
        const pxr::GfVec3d position(px, py, pz);
        const pxr::GfVec3f rotation(0.0f, 0.0f, 0.0f);
        const pxr::GfVec3f scale(1);
        const std::string name = capsuleNames[i].GetString();
        pxr::UsdGeomCapsule capsule = samples::createCapsule(
            tiltXform.GetPrim(),
            name,
            pxr::UsdGeomTokens->x,
            capsuleWidth,
            capsuleRadius,
            position,
            rotation,
            scale,
            displayColor
        );

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(capsule.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(capsule.GetPrim());

        capsules.push_back(capsule);
    }

    // Connect the root and the first capsule with a FixedJoint to fix them in place.
    {
        pxr::UsdPrim body0 = baseXform.GetPrim();
        pxr::UsdPrim body1 = capsules[0].GetPrim();

        const auto fixedJointName = usdex::core::getValidChildName(jointsXform.GetPrim(), "FixedJoint_root");

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsFixedJoint(
            jointsXform.GetPrim(), // Parent prim.
            fixedJointName.GetString(), // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame // Joint frame.
        );
    }

    // Create a vector of joint names
    const std::vector<std::string> srcJointNames(capsuleCount, "PrismaticJoint");
    const auto jointNames = usdex::core::getValidChildNames(jointsXform.GetPrim(), srcJointNames);

    // Connect two capsules with physics joints.
    // The slide of a PrismaticJoint is primarily about the local X axis and limits are set in centimeters.
    const pxr::GfVec3f axis(1, 0, 0);
    const float lowerLimit = 0.0f;
    const float upperLimit = 40.0f;
    for (int i = 1; i < capsuleCount; i++)
    {
        const std::string name = jointNames[i].GetString();

        // The two prims to be connected.
        pxr::UsdPrim body0 = capsules[i - 1].GetPrim();
        pxr::UsdPrim body1 = capsules[i].GetPrim();

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsPrismaticJoint(
            jointsXform.GetPrim(), // Parent prim.
            name, // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame, // Joint frame.
            axis, // Axis.
            lowerLimit, // Lower limit.
            upperLimit // Upper limit.
        );
    }
}

//! Create simple physics spherical joints.
//!
//! @param stage Target stage
//! @param centerPos Center position of the base xform
//! @param capsuleCount Number of capsules
void simplePhysicsSphericalJoints(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos, const int capsuleCount = 3)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "SimpleSphericalJoints");
    pxr::UsdGeomXform baseXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    // Create an Xform to place the joints.
    const auto jointsName = usdex::core::getValidChildName(baseXform.GetPrim(), "joints");
    pxr::UsdGeomXform jointsXform = usdex::core::defineXform(baseXform.GetPrim(), jointsName.GetString());

    // Create a vector of capsule names
    const std::vector<std::string> srcCapsuleNames(capsuleCount, "capsule");
    const auto capsuleNames = usdex::core::getValidChildNames(baseXform.GetPrim(), srcCapsuleNames);

    // Create capsules with rigid body and collision.
    const float capsuleWidth = 80.0f;
    const float capsuleRadius = 10.0f;
    const float capsuleMargin = 2.0f;
    const float capsuleLengthX = capsuleWidth + capsuleRadius * 2.0f + capsuleMargin;
    double px = 0.0;
    const double py = 200.0;
    double pz = 0.0;

    std::vector<pxr::UsdGeomXformable> capsules;
    for (int i = 0; i < capsuleCount; i++, px += capsuleLengthX)
    {
        const pxr::GfVec3f displayColor = (i == 0) ? pxr::GfVec3f(1, 0, 0) : pxr::GfVec3f(0, 1, 0);
        const pxr::GfVec3d position(px, py, pz);
        const pxr::GfVec3f rotation(0.0f, 0.0f, 0.0f);
        const pxr::GfVec3f scale(1);
        const std::string name = capsuleNames[i].GetString();
        pxr::UsdGeomCapsule capsule = samples::createCapsule(
            baseXform.GetPrim(),
            name,
            pxr::UsdGeomTokens->x,
            capsuleWidth,
            capsuleRadius,
            position,
            rotation,
            scale,
            displayColor
        );

        // Set rigid body.
        pxr::UsdPhysicsRigidBodyAPI::Apply(capsule.GetPrim());

        // Set collision.
        pxr::UsdPhysicsCollisionAPI::Apply(capsule.GetPrim());

        capsules.push_back(capsule);
    }

    // Connect the root and the first capsule with a FixedJoint to fix them in place.
    {
        pxr::UsdPrim body0 = baseXform.GetPrim();
        pxr::UsdPrim body1 = capsules[0].GetPrim();

        const auto fixedJointName = usdex::core::getValidChildName(jointsXform.GetPrim(), "FixedJoint_root");

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsFixedJoint(
            jointsXform.GetPrim(), // Parent prim.
            fixedJointName.GetString(), // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame // Joint frame.
        );
    }

    // Create a vector of joint names
    const std::vector<std::string> srcJointNames(capsuleCount, "SphericalJoint");
    const auto jointNames = usdex::core::getValidChildNames(jointsXform.GetPrim(), srcJointNames);

    // Connect two capsules with physics joints.
    // The rotation of a SphericalJoint is primarily about the local X axis and limits are set in degrees.
    const float coneAngle0Limit = 45.0f;
    const float coneAngle1Limit = 20.0f;
    const pxr::GfVec3f axis(1, 0, 0);
    for (int i = 1; i < capsuleCount; i++)
    {
        const std::string name = jointNames[i].GetString();

        // The two prims to be connected.
        pxr::UsdPrim body0 = capsules[i - 1].GetPrim();
        pxr::UsdPrim body1 = capsules[i].GetPrim();

        // The center position and rotation of the physics joint in body1's local coordinate system.
        // Body0 will be automatically aligned to match this joint frame.
        const usdex::core::JointFrame jointFrame = { /* space */ usdex::core::JointFrame::Space::Body1,
                                                     /* position */ pxr::GfVec3d(-capsuleLengthX * 0.5, 0, 0),
                                                     /* orientation */ pxr::GfQuatd::GetIdentity() };

        // Create a physics fixed joint.
        usdex::core::definePhysicsSphericalJoint(
            jointsXform.GetPrim(), // Parent prim.
            name, // Joint name.
            body0, // Body0.
            body1, // Body1.
            jointFrame, // Joint frame.
            axis, // Axis.
            coneAngle0Limit, // Cone angle 0 limit.
            coneAngle1Limit // Cone angle 1 limit.
        );
    }
}

//! Create physics materials.
//!
//! @param stage Target stage
//! @param centerPos Center position of the base xform
void physicsMaterials(pxr::UsdStageRefPtr stage, const pxr::GfVec3d& centerPos)
{
    // Get the default prim
    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Create xform.
    pxr::GfTransform transform;
    transform.SetTranslation(centerPos);
    const auto groupName = usdex::core::getValidChildName(defaultPrim, "physicsMaterials");
    pxr::UsdGeomXform baseXform = usdex::core::defineXform(defaultPrim, groupName.GetString(), transform);

    const auto rampsName = usdex::core::getValidChildName(baseXform.GetPrim(), "ramps");
    const auto cubesName = usdex::core::getValidChildName(baseXform.GetPrim(), "cubes");
    pxr::UsdGeomXform rampsXform = usdex::core::defineXform(baseXform.GetPrim(), rampsName.GetString());
    pxr::UsdGeomXform cubesXform = usdex::core::defineXform(baseXform.GetPrim(), cubesName.GetString());

    // Create a vector of ramp names
    const auto rampNames = usdex::core::getValidChildNames(rampsXform.GetPrim(), { "ramp", "ramp", "ramp" });

    // Create a vector of cube names
    const auto cubeNames = usdex::core::getValidChildNames(cubesXform.GetPrim(), { "cube", "cube", "cube" });

    // Here we will drop a ball onto an inclined ramp to check the friction caused by the physics material.
    // Create cube with rigid body and collision.
    std::vector<pxr::UsdGeomXformable> ramps;
    std::vector<pxr::UsdGeomXformable> cubes;
    for (int i = 0; i < 3; i++)
    {
        double pz = -100.0 + i * 100.0;
        // Create a ramp. This does not assign a rigid body, only collision.
        {
            const std::string name = rampNames[i].GetString();
            const pxr::GfVec3f displayColor(0, 1, 0);
            const pxr::GfVec3d position(20, 20, pz);
            const pxr::GfVec3f rotation(0, 0, -10.0f);
            const pxr::GfVec3f scale(2.5f, 0.05f, 0.8f);
            pxr::UsdGeomCube cube = samples::createCube(rampsXform.GetPrim(), name, 100.0f, position, rotation, scale, displayColor);

            // Set collision.
            pxr::UsdPhysicsCollisionAPI::Apply(cube.GetPrim());

            ramps.push_back(cube);
        }

        // Create a cube.
        {
            const std::string name = cubeNames[i].GetString();
            const pxr::GfVec3f displayColor(0, 0, 1);
            const pxr::GfVec3d position(-60, 160, pz);
            const pxr::GfVec3f rotation(0, 0, 0);
            const pxr::GfVec3f scale(1);
            pxr::UsdGeomCube cube = samples::createCube(cubesXform.GetPrim(), name, 30.0f, position, rotation, scale, displayColor);

            // Set rigid body.
            pxr::UsdPhysicsRigidBodyAPI::Apply(cube.GetPrim());

            // Set collision.
            pxr::UsdPhysicsCollisionAPI::Apply(cube.GetPrim());

            cubes.push_back(cube);
        }
    }

    const auto physicsMaterialsScopeName = usdex::core::getValidChildName(baseXform.GetPrim(), "physicsMaterials");
    pxr::UsdGeomScope physicsMaterialsScope = usdex::core::defineScope(baseXform.GetPrim(), physicsMaterialsScopeName);
    pxr::UsdPrim scopePrim = physicsMaterialsScope.GetPrim();
    std::vector<pxr::UsdShadeMaterial> materials;

    // Create a vector of physics material names
    const auto physicsMaterialNames = usdex::core::getValidChildNames(scopePrim, { "slippery", "rough", "bouncy" });

    // Creates a frictionless, slippery physics material.
    {
        const std::string name = physicsMaterialNames[0].GetString();
        const float dynamicFriction = 0.0f;
        const float staticFriction = 0.0f;
        const float restitution = 0.0f;
        const float density = 0.0f;
        pxr::UsdShadeMaterial material = usdex::core::definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density);
        materials.push_back(material);
    }

    // Creates a physics material with friction.
    {
        const std::string name = physicsMaterialNames[1].GetString();
        const float dynamicFriction = 0.9f;
        const float staticFriction = 0.9f;
        const float restitution = 0.0f;
        const float density = 0.0f;
        pxr::UsdShadeMaterial material = usdex::core::definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density);
        materials.push_back(material);
    }

    // Creates a physics material with strong bounciness.
    {
        const std::string name = physicsMaterialNames[2].GetString();
        const float dynamicFriction = 0.0f;
        const float staticFriction = 0.0f;
        const float restitution = 0.7f;
        const float density = 0.0f;
        pxr::UsdShadeMaterial material = usdex::core::definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density);
        materials.push_back(material);
    }

    // Bind physics material.
    // Assign the same physics material to the ramp and the cube.
    // When a collision occurs, friction is handled using the average value of the two physics materials.
    usdex::core::bindPhysicsMaterial(ramps[0].GetPrim(), materials[0]);
    usdex::core::bindPhysicsMaterial(cubes[0].GetPrim(), materials[0]);
    usdex::core::bindPhysicsMaterial(ramps[1].GetPrim(), materials[1]);
    usdex::core::bindPhysicsMaterial(cubes[1].GetPrim(), materials[1]);
    usdex::core::bindPhysicsMaterial(ramps[2].GetPrim(), materials[2]);
    usdex::core::bindPhysicsMaterial(cubes[2].GetPrim(), materials[2]);
}


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createPhysics", "Creates physics stage using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    // Create physics scene
    createPhysicsScene(stage);

    // Create ground with collision.
    if (!createGroundWithCollision(stage))
    {
        std::cout << "Error creating ground, exiting" << std::endl;
        return -1;
    }

    // Simple rigid bodies and collisions.
    // -830 > -610
    simpleRigidBodiesAndCollisions(stage, pxr::GfVec3d(-250, 0, -820));

    // Simple FixedJoint.
    simplePhysicsFixedJoints(stage, pxr::GfVec3d(-150, 0, -660));
    // Simple RevoluteJoint.
    simplePhysicsRevoluteJoints(stage, pxr::GfVec3d(-150, 0, -610));
    // Simple PrismaticJoint.
    simplePhysicsPrismaticJoints(stage, pxr::GfVec3d(-150, 0, -560));
    // Simple SphericalJoint.
    simplePhysicsSphericalJoints(stage, pxr::GfVec3d(-150, 0, -510));

    // physics materials.
    physicsMaterials(stage, pxr::GfVec3d(200, 0, -820));

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
