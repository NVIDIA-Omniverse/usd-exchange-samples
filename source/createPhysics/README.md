# OpenUSD Exchange Samples: createPhysics

This example demonstrates how to create rigid body or collision assignments, [physics joints](https://openusd.org/release/api/usd_physics_page_front.html#usdPhysics_joint_descriptor), and [physics materials](https://openusd.org/release/api/usd_physics_page_front.html#usdPhysics_physics_materials) using the OpenUSD Exchange SDK.  


## USD Modules

The Gf, Usd, UsdGeom, and UsdPhysics modules are used.


## OpenUSD Exchange SDK functions

- bindPhysicsMaterial()
- definePhysicsFixedJoint()
- definePhysicsMaterial()
- definePhysicsPrismaticJoint()
- definePhysicsRevoluteJoint()
- definePhysicsSphericalJoint()
- defineXform()
- saveStage()
- setLocalTransform()


## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createPhysics`
- `[./]python.[bat, sh] source/createPhysics/createPhysics.py`

## Hardcoded items

- The stage is created with a Y-up axis, 1 cm linear units, default Scope prim named "World"
- A PhysicsScene is created.
- A plane is created and collisions are assigned.
- A sphere with a radius of 30 cm and a cube with a side length of 50 cm are created, each with its own rigid body and collision.
- Three capsules with a height of 80 cm and a radius of 10 cm are created and connected with FixedJoints. Each capsule is assigned a rigid body and collisions. The first capsule is connected to the parent Xform with a FixedJoint.
- Three capsules with a height of 80 cm and a radius of 10 cm are created and connected with RevoluteJoints. Each capsule is assigned a rigid body and collisions. The first capsule is connected to the parent Xform with a FixedJoint.
- Three capsules are created in the same way and connected with RevoluteJoints.
- Three capsules are created in the same way and connected with PrismaticJoints. These capsules are tilted downwards so that we can easily see the slider-like movement when simulating.
- Three capsules are created in the same way and connected with SphericalJoints.
- Comparing three types of physics materials. We can see physics materials with no friction, high friction, and high bounce coefficients.
  - A tilted 250 cm x 5 cm x 80 cm cube(ramp) is created and collisions are assigned.
  - A cube with a size of 30 cm is created on top of it. It has rigid bodies and collisions assigned to it.
  - Three physics materials with different parameters are created.
  - The ramp and cube are assigned their respective physics materials.


## Command Line Arguments

```
Usage:
  createPhysics [OPTION...]

  -a, --usda             Output a text stage rather than binary
  -h, --help             Print usage
  -p, --path arg         Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
