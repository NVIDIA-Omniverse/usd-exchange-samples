# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import shutil
import tempfile
import unittest

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom, UsdPhysics, UsdShade, UsdUtils
from utils.BaseTestCase import BaseTestCase


class CreatePhysicsTestCase(BaseTestCase):
    # Check the physics joint parameters.
    def assertIsPhysicsJoint(
        self,
        joint: UsdPhysics.Joint,
        localPos0: Gf.Vec3f,
        localRot0: Gf.Quatf,
        localPos1: Gf.Vec3f,
        localRot1: Gf.Quatf,
        axis: str = None,
        lower_limit: float = None,
        upper_limit: float = None,
        coneAngle0Limit: float = None,
        coneAngle1Limit: float = None,
    ):
        self.assertTrue(joint.GetLocalPos0Attr().HasAuthoredValue())
        self.assertTrue(joint.GetLocalRot0Attr().HasAuthoredValue())
        self.assertTrue(joint.GetLocalPos1Attr().HasAuthoredValue())
        self.assertTrue(joint.GetLocalRot1Attr().HasAuthoredValue())

        _localPos0: Gf.Vec3f = joint.GetLocalPos0Attr().Get()
        _localRot0: Gf.Quatf = joint.GetLocalRot0Attr().Get()
        _localPos1: Gf.Vec3f = joint.GetLocalPos1Attr().Get()
        _localRot1: Gf.Quatf = joint.GetLocalRot1Attr().Get()

        self.assertTrue(Gf.IsClose(_localPos0, localPos0, 1e-6))
        self.assertTrue(Gf.IsClose(_localPos1, localPos1, 1e-6))
        self.assertAlmostEqual(_localRot0.GetReal(), localRot0.GetReal(), places=6)
        self.assertTrue(Gf.IsClose(_localRot0.GetImaginary(), localRot0.GetImaginary(), 1e-6))
        self.assertAlmostEqual(_localRot1.GetReal(), localRot1.GetReal(), places=6)
        self.assertTrue(Gf.IsClose(_localRot1.GetImaginary(), localRot1.GetImaginary(), 1e-6))

        prim = joint.GetPrim()
        if prim.IsA(UsdPhysics.RevoluteJoint) or prim.IsA(UsdPhysics.PrismaticJoint) or prim.IsA(UsdPhysics.SphericalJoint):
            if axis is not None:
                self.assertTrue(joint.GetAxisAttr().HasAuthoredValue())
                self.assertEqual(joint.GetAxisAttr().Get(), axis)
            else:
                self.assertFalse(joint.GetAxisAttr().HasAuthoredValue())

        if prim.IsA(UsdPhysics.RevoluteJoint) or prim.IsA(UsdPhysics.PrismaticJoint):
            if lower_limit is not None:
                self.assertTrue(joint.GetLowerLimitAttr().HasAuthoredValue())
                self.assertAlmostEqual(joint.GetLowerLimitAttr().Get(), lower_limit, places=4)
            else:
                self.assertFalse(joint.GetLowerLimitAttr().HasAuthoredValue())

            if upper_limit is not None:
                self.assertTrue(joint.GetUpperLimitAttr().HasAuthoredValue())
                self.assertAlmostEqual(joint.GetUpperLimitAttr().Get(), upper_limit, places=4)
            else:
                self.assertFalse(joint.GetUpperLimitAttr().HasAuthoredValue())

        if prim.IsA(UsdPhysics.SphericalJoint):
            if coneAngle0Limit is not None:
                self.assertTrue(joint.GetConeAngle0LimitAttr().HasAuthoredValue())
                self.assertAlmostEqual(joint.GetConeAngle0LimitAttr().Get(), coneAngle0Limit, places=4)
            else:
                self.assertFalse(joint.GetConeAngle0LimitAttr().HasAuthoredValue())

            if coneAngle1Limit is not None:
                self.assertTrue(joint.GetConeAngle1LimitAttr().HasAuthoredValue())
                self.assertAlmostEqual(joint.GetConeAngle1LimitAttr().Get(), coneAngle1Limit, places=4)
            else:
                self.assertFalse(joint.GetConeAngle1LimitAttr().HasAuthoredValue())

    # Check whether the physics material is stored correctly.
    def assertIsPhysicsMaterial(self, material: UsdShade.Material, dynamicFriction: float, staticFriction: float, restitution: float, density: float):
        self.assertTrue(material.GetPrim().HasAPI(UsdPhysics.MaterialAPI))
        materialAPI = UsdPhysics.MaterialAPI(material.GetPrim())

        attr = materialAPI.GetDensityAttr()
        self.assertTrue(attr.IsDefined())
        self.assertTrue(attr.HasAuthoredValue())
        self.assertAlmostEqual(attr.Get(), density, places=6)

        attr = materialAPI.GetDynamicFrictionAttr()
        self.assertTrue(attr.IsDefined())
        self.assertTrue(attr.HasAuthoredValue())
        self.assertAlmostEqual(attr.Get(), dynamicFriction, places=6)

        attr = materialAPI.GetStaticFrictionAttr()
        self.assertTrue(attr.IsDefined())
        self.assertTrue(attr.HasAuthoredValue())
        self.assertAlmostEqual(attr.Get(), staticFriction, places=6)

        attr = materialAPI.GetRestitutionAttr()
        self.assertTrue(attr.IsDefined())
        self.assertTrue(attr.HasAuthoredValue())
        self.assertAlmostEqual(attr.Get(), restitution, places=6)

    # Test the createPhysics program
    def _checkStageContents(self, stagePath):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        primNames = [
            "PhysicsScene",
            "ground",
            "SimpleRigidBodies",
            "SimpleFixedJoints",
            "SimpleRevoluteJoints",
            "SimplePrismaticJoints",
            "SimpleSphericalJoints",
            "physicsMaterials",
        ]

        for primName in primNames:
            if primName == "PhysicsScene":
                # Check the PhysicsScene.
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/PhysicsScene")
                self.assertTrue(prim)
                self.assertTrue(prim.IsA(UsdPhysics.Scene))

            elif primName == "ground":
                # Check if collision exist.
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/ground")
                self.assertTrue(prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertFalse(prim.HasAPI(UsdPhysics.RigidBodyAPI))

            elif primName == "SimpleRigidBodies":
                # Check if collision and rigid body exist.
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/SimpleRigidBodies")
                self.assertTrue(prim)
                spherePrim = stage.GetPrimAtPath(f"{prim.GetPath()}/sphere")
                self.assertTrue(spherePrim)
                self.assertTrue(spherePrim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(spherePrim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                cubePrim = stage.GetPrimAtPath(f"{prim.GetPath()}/cube")
                self.assertTrue(spherePrim)
                self.assertTrue(spherePrim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(spherePrim.HasAPI(UsdPhysics.CollisionAPI))

            elif primName == "SimpleFixedJoints":
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/SimpleFixedJoints")
                self.assertTrue(prim)

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_1")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_2")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_root")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(-51, 200, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_1")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_2")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

            elif primName == "SimpleRevoluteJoints":
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/SimpleRevoluteJoints")
                self.assertTrue(prim)

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_1")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_2")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_root")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(-51, 200, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

                # Check the RevoluteJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/RevoluteJoint_1")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.RevoluteJoint))
                joint = UsdPhysics.RevoluteJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                lowerLimit = -45.0
                upperLimit = 20.0
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.z, lowerLimit, upperLimit)

                # Check the RevoluteJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/RevoluteJoint_2")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.RevoluteJoint))
                joint = UsdPhysics.RevoluteJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                lowerLimit = -45.0
                upperLimit = 20.0
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.z, lowerLimit, upperLimit)

            elif primName == "SimplePrismaticJoints":
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/SimplePrismaticJoints")
                self.assertTrue(prim)

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/tilt/capsule")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/tilt/capsule_1")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/tilt/capsule_2")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_root")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(-48.49841, 206.38493, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(0.9914449, 0, 0, -0.13052619)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

                # Check the PrismaticJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/PrismaticJoint_1")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.PrismaticJoint))
                joint = UsdPhysics.PrismaticJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                lowerLimit = 0.0
                upperLimit = 40.0
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.x, lowerLimit, upperLimit)

                # Check the PrismaticJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/PrismaticJoint_2")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.PrismaticJoint))
                joint = UsdPhysics.PrismaticJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                lowerLimit = 0.0
                upperLimit = 40.0
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.x, lowerLimit, upperLimit)

            elif primName == "SimpleSphericalJoints":
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/SimpleSphericalJoints")
                self.assertTrue(prim)

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_1")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check if collision and rigid body exist.
                capsule_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/capsule_2")
                self.assertTrue(capsule_prim)
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.RigidBodyAPI))
                self.assertTrue(capsule_prim.HasAPI(UsdPhysics.CollisionAPI))

                # Check the FixedJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/FixedJoint_root")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.FixedJoint))
                joint = UsdPhysics.FixedJoint(joint_prim)

                localPos0 = Gf.Vec3f(-51, 200, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                self.assertIsPhysicsJoint(joint, localPos0, localRot0, localPos1, localRot1)

                # Check the SphericalJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/SphericalJoint_1")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.SphericalJoint))
                joint = UsdPhysics.SphericalJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                coneAngle0Limit = 45.0
                coneAngle1Limit = 20.0
                self.assertIsPhysicsJoint(
                    joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.x, None, None, coneAngle0Limit, coneAngle1Limit
                )

                # Check the SphericalJoint.
                joint_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/joints/SphericalJoint_2")
                self.assertTrue(joint_prim)
                self.assertTrue(joint_prim.IsA(UsdPhysics.SphericalJoint))
                joint = UsdPhysics.SphericalJoint(joint_prim)

                localPos0 = Gf.Vec3f(51, 0, 0)
                localPos1 = Gf.Vec3f(-51, 0, 0)
                localRot0 = Gf.Quatf(1, 0, 0, 0)
                localRot1 = Gf.Quatf(1, 0, 0, 0)
                coneAngle0Limit = 45.0
                coneAngle1Limit = 20.0
                self.assertIsPhysicsJoint(
                    joint, localPos0, localRot0, localPos1, localRot1, UsdGeom.Tokens.x, None, None, coneAngle0Limit, coneAngle1Limit
                )

            elif primName == "physicsMaterials":
                prim = stage.GetPrimAtPath(f"{defaultPrim.GetPath()}/physicsMaterials")
                self.assertTrue(prim)

                # Check the physicsMaterials.
                material1_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/physicsMaterials/slippery")
                material2_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/physicsMaterials/rough")
                material3_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/physicsMaterials/bouncy")
                self.assertTrue(material1_prim)
                self.assertTrue(material2_prim)
                self.assertTrue(material3_prim)
                self.assertTrue(material1_prim.IsA(UsdShade.Material))
                self.assertTrue(material2_prim.IsA(UsdShade.Material))
                self.assertTrue(material3_prim.IsA(UsdShade.Material))
                self.assertTrue(material1_prim.HasAPI(UsdPhysics.MaterialAPI))
                self.assertTrue(material2_prim.HasAPI(UsdPhysics.MaterialAPI))
                self.assertTrue(material3_prim.HasAPI(UsdPhysics.MaterialAPI))

                # Check the physics material parameters.
                self.assertIsPhysicsMaterial(material1_prim, 0.0, 0.0, 0.0, 0.0)
                self.assertIsPhysicsMaterial(material2_prim, 0.9, 0.9, 0.0, 0.0)
                self.assertIsPhysicsMaterial(material3_prim, 0.0, 0.0, 0.7, 0.0)

                # Checks if the specified prim has a physics material.
                plane_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/ramps/ramp")
                self.assertTrue(plane_prim)
                self.assertTrue(plane_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(plane_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(plane_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material1_prim.GetPrim().GetPath())

                # Checks if the specified prim has a physics material.
                plane_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/ramps/ramp_1")
                self.assertTrue(plane_prim)
                self.assertTrue(plane_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(plane_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(plane_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material2_prim.GetPrim().GetPath())

                # Checks if the specified prim has a physics material.
                plane_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/ramps/ramp_2")
                self.assertTrue(plane_prim)
                self.assertTrue(plane_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(plane_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(plane_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material3_prim.GetPrim().GetPath())

                # Checks if the specified prim has a physics material.
                cube_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/cubes/cube")
                self.assertTrue(cube_prim)
                self.assertTrue(cube_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(cube_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(cube_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material1_prim.GetPrim().GetPath())

                # Checks if the specified prim has a physics material.
                cube_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/cubes/cube_1")
                self.assertTrue(cube_prim)
                self.assertTrue(cube_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(cube_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(cube_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material2_prim.GetPrim().GetPath())

                # Checks if the specified prim has a physics material.
                cube_prim = stage.GetPrimAtPath(f"{prim.GetPath()}/cubes/cube_2")
                self.assertTrue(cube_prim)
                self.assertTrue(cube_prim.HasAPI(UsdPhysics.CollisionAPI))
                self.assertTrue(cube_prim.HasAPI(UsdShade.MaterialBindingAPI))

                materialBindingAPI = UsdShade.MaterialBindingAPI(cube_prim.GetPrim())
                rel = materialBindingAPI.GetDirectBindingRel("physics")
                pathList = rel.GetTargets()
                self.assertEqual(len(pathList), 1)
                self.assertEqual(pathList[0], material3_prim.GetPrim().GetPath())

    def _runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]

            for args in argsRuns:
                if args[1]:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                else:
                    return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                self.assertEqual(return_code, 0, output)
                self._checkStageContents(args[0])
                utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)

    def testCppCreateMaterials(self):
        self._runSampleOptions("run", "createPhysics")

    def testPythonCreateMaterials(self):
        self._runSampleOptions("python", "source/createPhysics/createPhysics.py")

    def testCompareTextCreateMaterials(self):
        self.compareTextOutput("createPhysics", "source/createPhysics/createPhysics.py")
