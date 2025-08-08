# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from pxr import Gf, Usd, UsdGeom, UsdPhysics


# Create a physics scene.
#
# @param stage Target stage
def createPhysicsScene(stage: Usd.Stage):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Check if the physics scene already exists, we only want one per stage.
    for prim in Usd.PrimRange(defaultPrim):
        if prim.IsA(UsdPhysics.Scene):
            return

    # Create physics scene, note that we don't have to specify gravity because
    # the default value is derived from the stage's upAxis and linear scale.
    # In this case the gravity would be (0.0, -981.0, 0.0) since the stage has a
    # Y upAxis with a centimeter linear scale.
    physicsSceneName = usdex.core.getValidChildName(defaultPrim, "PhysicsScene")
    scenePath = defaultPrim.GetPath().AppendChild(physicsSceneName)
    UsdPhysics.Scene.Define(stage, scenePath)


# Create a ground plane with collision assigned.
#
# @param stage A valid stage to create the ground plane in
#
# @returns True if the ground plane was created successfully, false otherwise
def createGroundWithCollision(stage: Usd.Stage) -> bool:
    defaultPrim = stage.GetDefaultPrim()

    # Check if the plane already exists, we only want one per stage.
    for prim in Usd.PrimRange(defaultPrim):
        if prim.IsA(UsdGeom.Plane):
            return True

    groundName = usdex.core.getValidChildName(defaultPrim, "ground")
    groundPath = defaultPrim.GetPath().AppendChild(groundName)
    plane = UsdGeom.Plane.Define(stage, groundPath)
    if not plane:
        return False

    plane.GetAxisAttr().Set(UsdGeom.GetStageUpAxis(stage))

    # Set collider.
    UsdPhysics.CollisionAPI.Apply(plane.GetPrim())

    # Set transform.
    position = Gf.Vec3d(0, -50, 0)
    pivot = Gf.Vec3d(0)
    rotation = Gf.Vec3f(0, 0, 0)
    scale = Gf.Vec3f(1, 1, 1)
    usdex.core.setLocalTransform(plane, position, pivot, rotation, usdex.core.RotationOrder.eXyz, scale)

    return True


# Create simple rigid bodies and collisions.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
def simpleRigidBodiesAndCollisions(stage: Usd.Stage, centerPos: Gf.Vec3d):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "SimpleRigidBodies")
    simpleXform = usdex.core.defineXform(defaultPrim, groupName, transform)

    # Create sphere with rigid body and collision.
    displayColor = Gf.Vec3f(1, 0, 0)
    position = Gf.Vec3d(0, 200, 0)
    rotation = Gf.Vec3f(0)
    scale = Gf.Vec3f(1)
    sphere = common.usdUtils.createSphere(simpleXform.GetPrim(), "sphere", 30.0, position, rotation, scale, displayColor)

    # Set rigid body.
    UsdPhysics.RigidBodyAPI.Apply(sphere.GetPrim())

    # Set collision.
    UsdPhysics.CollisionAPI.Apply(sphere.GetPrim())

    # Create cube with rigid body and collision.
    displayColor = Gf.Vec3f(0, 1, 0)
    position = Gf.Vec3d(120, 250, 0)
    rotation = Gf.Vec3f(50, 45, 0)
    scale = Gf.Vec3f(1)
    cube = common.usdUtils.createCube(simpleXform.GetPrim(), "cube", 50.0, position, rotation, scale, displayColor)

    # Set rigid body.
    UsdPhysics.RigidBodyAPI.Apply(cube.GetPrim())

    # Set collision.
    UsdPhysics.CollisionAPI.Apply(cube.GetPrim())


# Create simple physics fixed joints.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
# @param capsuleCount Number of capsules
def simplePhysicsFixedJoints(stage: Usd.Stage, centerPos: Gf.Vec3d, capsuleCount: int = 3):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "SimpleFixedJoints")
    baseXform = usdex.core.defineXform(defaultPrim, groupName, transform)

    # Create an Xform to place the joints.
    jointsName = usdex.core.getValidChildName(baseXform.GetPrim(), "joints")
    jointsXform = usdex.core.defineXform(baseXform.GetPrim(), jointsName)

    # Create a vector of capsule names
    srcCapsuleNames = ["capsule"] * capsuleCount
    capsuleNames = usdex.core.getValidChildNames(baseXform.GetPrim(), srcCapsuleNames)

    # Create capsules with rigid body and collision.
    capsuleWidth = 80.0
    capsuleRadius = 10.0
    capsuleMargin = 2.0
    capsuleLengthX = capsuleWidth + capsuleRadius * 2.0 + capsuleMargin
    px = 0.0
    py = 200.0
    pz = 0.0

    capsules = []
    for i in range(capsuleCount):
        displayColor = Gf.Vec3f(1, 0, 0) if i == 0 else Gf.Vec3f(0, 1, 0)
        position = Gf.Vec3d(px, py, pz)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1)
        name = capsuleNames[i]
        capsule = common.usdUtils.createCapsule(
            baseXform.GetPrim(), name, UsdGeom.Tokens.x, capsuleWidth, capsuleRadius, position, rotation, scale, displayColor
        )

        # Set rigid body.
        UsdPhysics.RigidBodyAPI.Apply(capsule.GetPrim())

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(capsule.GetPrim())

        capsules.append(capsule)
        px += capsuleLengthX

    # Connect the root and the first capsule with a FixedJoint to fix them in place.
    body0 = baseXform.GetPrim()
    body1 = capsules[0].GetPrim()

    name = "FixedJoint_root"

    # The center position and rotation of the physics joint in body1's local coordinate system.
    # Body0 will be automatically aligned to match this joint frame.
    jointFrame = usdex.core.JointFrame(
        usdex.core.JointFrame.Space.Body1,  # Space.
        Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
        Gf.Quatd.GetIdentity(),  # Orientation.
    )

    # Create a physics fixed joint.
    usdex.core.definePhysicsFixedJoint(jointsXform.GetPrim(), name, body0, body1, jointFrame)

    # Create a vector of joint names
    srcJointNames = ["FixedJoint"] * capsuleCount
    jointNames = usdex.core.getValidChildNames(jointsXform.GetPrim(), srcJointNames)

    # Connect two capsules with physics joints.
    for i in range(1, capsuleCount):
        name = jointNames[i]

        # The two prims to be connected.
        body0 = capsules[i - 1].GetPrim()
        body1 = capsules[i].GetPrim()

        # The center position and rotation of the physics joint in body1's local coordinate system.
        # Body0 will be automatically aligned to match this joint frame.
        jointFrame = usdex.core.JointFrame(
            usdex.core.JointFrame.Space.Body1,  # Space.
            Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
            Gf.Quatd.GetIdentity(),  # Orientation.
        )

        # Create a physics fixed joint.
        usdex.core.definePhysicsFixedJoint(jointsXform.GetPrim(), name, body0, body1, jointFrame)


# Create simple physics revolute joints.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
# @param capsuleCount Number of capsules
def simplePhysicsRevoluteJoints(stage: Usd.Stage, centerPos: Gf.Vec3d, capsuleCount: int = 3):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "SimpleRevoluteJoints")
    baseXform = usdex.core.defineXform(defaultPrim, groupName, transform)

    # Create an Xform to place the joints.
    jointsName = usdex.core.getValidChildName(baseXform.GetPrim(), "joints")
    jointsXform = usdex.core.defineXform(baseXform.GetPrim(), jointsName)

    # Create a vector of capsule names
    srcCapsuleNames = ["capsule"] * capsuleCount
    capsuleNames = usdex.core.getValidChildNames(baseXform.GetPrim(), srcCapsuleNames)

    # Create capsules with rigid body and collision.
    capsuleWidth = 80.0
    capsuleRadius = 10.0
    capsuleMargin = 2.0
    capsuleLengthX = capsuleWidth + capsuleRadius * 2.0 + capsuleMargin
    px = 0.0
    py = 200.0
    pz = 0.0

    capsules = []
    for i in range(capsuleCount):
        displayColor = Gf.Vec3f(1, 0, 0) if i == 0 else Gf.Vec3f(0, 1, 0)
        position = Gf.Vec3d(px, py, pz)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1)
        name = capsuleNames[i]
        capsule = common.usdUtils.createCapsule(
            baseXform.GetPrim(), name, UsdGeom.Tokens.x, capsuleWidth, capsuleRadius, position, rotation, scale, displayColor
        )

        # Set rigid body.
        UsdPhysics.RigidBodyAPI.Apply(capsule.GetPrim())

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(capsule.GetPrim())

        capsules.append(capsule)
        px += capsuleLengthX

    # Connect the root and the first capsule with a FixedJoint to fix them in place.
    body0 = baseXform.GetPrim()
    body1 = capsules[0].GetPrim()

    name = usdex.core.getValidChildName(jointsXform.GetPrim(), "FixedJoint_root")

    # The center position and rotation of the physics joint in body1's local coordinate system.
    # Body0 will be automatically aligned to match this joint frame.
    jointFrame = usdex.core.JointFrame(
        usdex.core.JointFrame.Space.Body1,  # Space.
        Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
        Gf.Quatd.GetIdentity(),  # Orientation.
    )

    # Create a physics fixed joint.
    usdex.core.definePhysicsFixedJoint(jointsXform.GetPrim(), name, body0, body1, jointFrame)

    # Create a vector of joint names
    srcJointNames = ["RevoluteJoint"] * capsuleCount
    jointNames = usdex.core.getValidChildNames(jointsXform.GetPrim(), srcJointNames)

    # Connect two capsules with physics joints.
    # The rotation of a RevoluteJoint is primarily about the local Z axis and limits are set in degrees.
    lowerLimit = -45.0
    upperLimit = 20.0
    axis = Gf.Vec3f(0, 0, 1)
    for i in range(1, capsuleCount):
        name = jointNames[i]

        # The two prims to be connected.
        body0 = capsules[i - 1].GetPrim()
        body1 = capsules[i].GetPrim()

        # The center position and rotation of the physics joint in body1's local coordinate system.
        # Body0 will be automatically aligned to match this joint frame.
        jointFrame = usdex.core.JointFrame(
            usdex.core.JointFrame.Space.Body1,  # Space.
            Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
            Gf.Quatd.GetIdentity(),  # Orientation.
        )

        # Create a physics fixed joint.
        usdex.core.definePhysicsRevoluteJoint(
            jointsXform.GetPrim(),  # Parent prim.
            name,  # Joint name.
            body0,  # Body0.
            body1,  # Body1.
            jointFrame,  # Joint frame.
            axis,  # Axis.
            lowerLimit,  # Lower limit.
            upperLimit,  # Upper limit.
        )


# Create simple physics prismatic joints.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
# @param capsuleCount Number of capsules
def simplePhysicsPrismaticJoints(stage: Usd.Stage, centerPos: Gf.Vec3d, capsuleCount: int = 3):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "SimplePrismaticJoints")
    baseXform = usdex.core.defineXform(defaultPrim, groupName, transform)

    # Create an Xform to place the joints.
    jointsName = usdex.core.getValidChildName(baseXform.GetPrim(), "joints")
    jointsXform = usdex.core.defineXform(baseXform.GetPrim(), jointsName)

    # Create capsules with rigid body and collision.
    capsuleWidth = 80.0
    capsuleRadius = 10.0
    capsuleMargin = 2.0
    capsuleLengthX = capsuleWidth + capsuleRadius * 2.0 + capsuleMargin
    px = 0.0
    py = 200.0
    pz = 0.0

    # Xform tilted slightly downwards.
    tiltTransform = Gf.Transform()
    tiltTransform.SetTranslation(Gf.Vec3d(-(capsuleLengthX * 0.5), 0, 0))
    tiltTransform.SetRotation(Gf.Rotation(Gf.Vec3d(0, 0, 1), -15.0))
    tiltXform = usdex.core.defineXform(baseXform.GetPrim(), "tilt", tiltTransform)

    # Create a vector of capsule names
    srcCapsuleNames = ["capsule"] * capsuleCount
    capsuleNames = usdex.core.getValidChildNames(tiltXform.GetPrim(), srcCapsuleNames)

    capsules = []
    for i in range(capsuleCount):
        displayColor = Gf.Vec3f(1, 0, 0) if i == 0 else Gf.Vec3f(0, 1, 0)
        position = Gf.Vec3d(px, py, pz)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1)
        name = capsuleNames[i]
        capsule = common.usdUtils.createCapsule(
            tiltXform.GetPrim(), name, UsdGeom.Tokens.x, capsuleWidth, capsuleRadius, position, rotation, scale, displayColor
        )

        # Set rigid body.
        UsdPhysics.RigidBodyAPI.Apply(capsule.GetPrim())

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(capsule.GetPrim())

        capsules.append(capsule)
        px += capsuleLengthX

    # Connect the root and the first capsule with a FixedJoint to fix them in place.
    body0 = baseXform.GetPrim()
    body1 = capsules[0].GetPrim()

    name = usdex.core.getValidChildName(jointsXform.GetPrim(), "FixedJoint_root")

    # The center position and rotation of the physics joint in body1's local coordinate system.
    # Body0 will be automatically aligned to match this joint frame.
    jointFrame = usdex.core.JointFrame(
        usdex.core.JointFrame.Space.Body1,  # Space.
        Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
        Gf.Quatd.GetIdentity(),  # Orientation.
    )

    # Create a physics fixed joint.
    usdex.core.definePhysicsFixedJoint(jointsXform.GetPrim(), name, body0, body1, jointFrame)

    # Create a vector of joint names
    srcJointNames = ["PrismaticJoint"] * capsuleCount
    jointNames = usdex.core.getValidChildNames(jointsXform.GetPrim(), srcJointNames)

    # Connect two capsules with physics joints.
    # The slide of a PrismaticJoint is primarily about the local X axis and limits are set in centimeters.
    axis = Gf.Vec3f(1, 0, 0)
    lowerLimit = 0.0
    upperLimit = 40.0
    for i in range(1, capsuleCount):
        name = jointNames[i]

        # The two prims to be connected.
        body0 = capsules[i - 1].GetPrim()
        body1 = capsules[i].GetPrim()

        # The center position and rotation of the physics joint in body1's local coordinate system.
        # Body0 will be automatically aligned to match this joint frame.
        jointFrame = usdex.core.JointFrame(
            usdex.core.JointFrame.Space.Body1,  # Space.
            Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
            Gf.Quatd.GetIdentity(),  # Orientation.
        )

        # Create a physics fixed joint.
        usdex.core.definePhysicsPrismaticJoint(
            jointsXform.GetPrim(),  # Parent prim.
            name,  # Joint name.
            body0,  # Body0.
            body1,  # Body1.
            jointFrame,  # Joint frame.
            axis,  # Axis.
            lowerLimit,  # Lower limit.
            upperLimit,  # Upper limit.
        )


# Create simple physics spherical joints.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
# @param capsuleCount Number of capsules
def simplePhysicsSphericalJoints(stage: Usd.Stage, centerPos: Gf.Vec3d, capsuleCount: int = 3):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "SimpleSphericalJoints")
    baseXform = usdex.core.defineXform(defaultPrim, groupName, transform)

    # Create an Xform to place the joints.
    jointsName = usdex.core.getValidChildName(baseXform.GetPrim(), "joints")
    jointsXform = usdex.core.defineXform(baseXform.GetPrim(), jointsName)

    # Create a vector of capsule names
    srcCapsuleNames = ["capsule"] * capsuleCount
    capsuleNames = usdex.core.getValidChildNames(baseXform.GetPrim(), srcCapsuleNames)

    # Create capsules with rigid body and collision.
    capsuleWidth = 80.0
    capsuleRadius = 10.0
    capsuleMargin = 2.0
    capsuleLengthX = capsuleWidth + capsuleRadius * 2.0 + capsuleMargin
    px = 0.0
    py = 200.0
    pz = 0.0

    capsules = []
    for i in range(capsuleCount):
        displayColor = Gf.Vec3f(1, 0, 0) if i == 0 else Gf.Vec3f(0, 1, 0)
        position = Gf.Vec3d(px, py, pz)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1)
        name = capsuleNames[i]
        capsule = common.usdUtils.createCapsule(
            baseXform.GetPrim(), name, UsdGeom.Tokens.x, capsuleWidth, capsuleRadius, position, rotation, scale, displayColor
        )

        # Set rigid body.
        UsdPhysics.RigidBodyAPI.Apply(capsule.GetPrim())

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(capsule.GetPrim())

        capsules.append(capsule)
        px += capsuleLengthX

    # Connect the root and the first capsule with a FixedJoint to fix them in place.
    body0 = baseXform.GetPrim()
    body1 = capsules[0].GetPrim()

    name = usdex.core.getValidChildName(jointsXform.GetPrim(), "FixedJoint_root")

    # The center position and rotation of the physics joint in body1's local coordinate system.
    # Body0 will be automatically aligned to match this joint frame.
    jointFrame = usdex.core.JointFrame(
        usdex.core.JointFrame.Space.Body1,  # Space.
        Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
        Gf.Quatd.GetIdentity(),  # Orientation.
    )

    # Create a physics fixed joint.
    usdex.core.definePhysicsFixedJoint(jointsXform.GetPrim(), name, body0, body1, jointFrame)

    # Create a vector of joint names
    srcJointNames = ["SphericalJoint"] * capsuleCount
    jointNames = usdex.core.getValidChildNames(jointsXform.GetPrim(), srcJointNames)

    # Connect two capsules with physics joints.
    # The rotation of a SphericalJoint is primarily about the local X axis and limits are set in degrees.
    coneAngle0Limit = 45.0
    coneAngle1Limit = 20.0
    axis = Gf.Vec3f(1, 0, 0)
    for i in range(1, capsuleCount):
        name = jointNames[i]

        # The two prims to be connected.
        body0 = capsules[i - 1].GetPrim()
        body1 = capsules[i].GetPrim()

        # The center position and rotation of the physics joint in body1's local coordinate system.
        # Body0 will be automatically aligned to match this joint frame.
        jointFrame = usdex.core.JointFrame(
            usdex.core.JointFrame.Space.Body1,  # Space.
            Gf.Vec3d(-capsuleLengthX * 0.5, 0, 0),  # Position.
            Gf.Quatd.GetIdentity(),  # Orientation.
        )

        # Create a physics fixed joint.
        usdex.core.definePhysicsSphericalJoint(
            jointsXform.GetPrim(),  # Parent prim.
            name,  # Joint name.
            body0,  # Body0.
            body1,  # Body1.
            jointFrame,  # Joint frame.
            axis,  # Axis.
            coneAngle0Limit,  # Cone angle 0 limit.
            coneAngle1Limit,  # Cone angle 1 limit.
        )


# Create physics materials.
#
# @param stage Target stage
# @param centerPos Center position of the base xform
def physicsMaterials(stage: Usd.Stage, centerPos: Gf.Vec3d):
    # Get the default prim
    defaultPrim = stage.GetDefaultPrim()

    # Create xform.
    transform = Gf.Transform()
    transform.SetTranslation(centerPos)
    groupName = usdex.core.getValidChildName(defaultPrim, "physicsMaterials")
    baseXform = usdex.core.defineXform(defaultPrim, groupName, transform)
    rampsName = usdex.core.getValidChildName(baseXform.GetPrim(), "ramps")
    cubesName = usdex.core.getValidChildName(baseXform.GetPrim(), "cubes")
    rampsXform = usdex.core.defineXform(baseXform.GetPrim(), rampsName)
    cubesXform = usdex.core.defineXform(baseXform.GetPrim(), cubesName)

    # Create a vector of ramp names
    rampNames = usdex.core.getValidChildNames(rampsXform.GetPrim(), ["ramp", "ramp", "ramp"])

    # Create a vector of cube names
    cubeNames = usdex.core.getValidChildNames(cubesXform.GetPrim(), ["cube", "cube", "cube"])

    # Here we will drop a ball onto an inclined ramp to check the friction caused by the physics material.
    # Create cube with rigid body and collision.
    ramps = []
    cubes = []
    for i in range(3):
        pz = -100.0 + i * 100.0
        # Create a ramp. This does not assign a rigid body, only collision.
        name = rampNames[i]
        displayColor = Gf.Vec3f(0, 1, 0)
        position = Gf.Vec3d(20, 20, pz)
        rotation = Gf.Vec3f(0, 0, -10.0)
        scale = Gf.Vec3f(2.5, 0.05, 0.8)
        cube = common.usdUtils.createCube(rampsXform.GetPrim(), name, 100.0, position, rotation, scale, displayColor)

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())

        ramps.append(cube)

        # Create a cube.
        name = cubeNames[i]
        displayColor = Gf.Vec3f(0, 0, 1)
        position = Gf.Vec3d(-60, 160, pz)
        rotation = Gf.Vec3f(0, 0, 0)
        scale = Gf.Vec3f(1)
        cube = common.usdUtils.createCube(cubesXform.GetPrim(), name, 30.0, position, rotation, scale, displayColor)

        # Set rigid body.
        UsdPhysics.RigidBodyAPI.Apply(cube.GetPrim())

        # Set collision.
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())

        cubes.append(cube)

    physicsMaterialsScopeName = usdex.core.getValidChildName(baseXform.GetPrim(), "physicsMaterials")
    physicsMaterialsScope = usdex.core.defineScope(baseXform.GetPrim(), physicsMaterialsScopeName)
    scopePrim = physicsMaterialsScope.GetPrim()
    materials = []

    # Create a vector of physics material names
    physicsMaterialNames = usdex.core.getValidChildNames(scopePrim, ["slippery", "rough", "bouncy"])

    # Creates a frictionless, slippery physics material.
    name = physicsMaterialNames[0]
    dynamicFriction = 0.0
    staticFriction = 0.0
    restitution = 0.0
    density = 0.0
    material = usdex.core.definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density)
    materials.append(material)

    # Creates a physics material with friction.
    name = physicsMaterialNames[1]
    dynamicFriction = 0.9
    staticFriction = 0.9
    restitution = 0.0
    density = 0.0
    material = usdex.core.definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density)
    materials.append(material)

    # Creates a physics material with strong bounciness.
    name = physicsMaterialNames[2]
    dynamicFriction = 0.0
    staticFriction = 0.0
    restitution = 0.7
    density = 0.0
    material = usdex.core.definePhysicsMaterial(scopePrim, name, dynamicFriction, staticFriction, restitution, density)
    materials.append(material)

    # Bind physics material.
    # Assign the same physics material to the ramp and the cube.
    # When a collision occurs, friction is handled using the average value of the two physics materials.
    usdex.core.bindPhysicsMaterial(ramps[0].GetPrim(), materials[0])
    usdex.core.bindPhysicsMaterial(cubes[0].GetPrim(), materials[0])
    usdex.core.bindPhysicsMaterial(ramps[1].GetPrim(), materials[1])
    usdex.core.bindPhysicsMaterial(cubes[1].GetPrim(), materials[1])
    usdex.core.bindPhysicsMaterial(ramps[2].GetPrim(), materials[2])
    usdex.core.bindPhysicsMaterial(cubes[2].GetPrim(), materials[2])


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    # Create physics scene
    createPhysicsScene(stage)

    # Create ground with collision.
    if not createGroundWithCollision(stage):
        print("Error creating ground, exiting")
        sys.exit(-1)

    # Simple rigid bodies and collisions.
    simpleRigidBodiesAndCollisions(stage, Gf.Vec3d(-250, 0, -820))

    # Simple FixedJoint.
    simplePhysicsFixedJoints(stage, Gf.Vec3d(-150, 0, -660))
    # Simple RevoluteJoint.
    simplePhysicsRevoluteJoints(stage, Gf.Vec3d(-150, 0, -610))
    # Simple PrismaticJoint.
    simplePhysicsPrismaticJoints(stage, Gf.Vec3d(-150, 0, -560))
    # Simple SphericalJoint.
    simplePhysicsSphericalJoints(stage, Gf.Vec3d(-150, 0, -510))

    # physics materials.
    physicsMaterials(stage, Gf.Vec3d(200, 0, -820))

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a physics joints and physics materials using the OpenUSD Exchange SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(common.commandLine.parseCommonOptions(parser))
