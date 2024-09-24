# OpenUSD Exchange Samples: createSkeleton

This sample demonstrates how to open/create a stage with key metadata and create skeletal mesh with an animation using the OpenUSD Exchange SDK.

The [OpenUSD documentation for using the UsdSkel API](https://openusd.org/release/api/_usd_skel__a_p_i__intro.html) is very thorough and should be used as both an introduction and reference. This sample creates a [UsdSkelRoot](https://openusd.org/release/api/class_usd_skel_root.html) parent prim with a [UsdSkelAnimation](https://openusd.org/release/api/class_usd_skel_animation.html) bound to a [UsdSkelSkeleton](https://openusd.org/release/api/class_usd_skel_skeleton.html).  Then a [UsdSkelBindingAPI](https://openusd.org/release/api/class_usd_skel_binding_a_p_i.html) is applied to a UsdGeomMesh and the skeleton joint indices and weights are applied. The result is a square "arm" with shoulder (j0), elbow (j1), and wrist(j2) joints.  The sample animation contains timesamples for the elbow and wrist joints.

A diagram representing the vertices and joints in the skeletal mesh:
```
2---j2---3
|   |    |
1---j1---4
|   |    |
0---j0---5
```

## USD Modules

The Gf, Sdf, Usd, UsdGeom, UsdSkel, and Vt modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- definePolyMesh()
- getValidChildNames()
- saveStage()
- setLocalTransform()
- Vec3fPrimvarData()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createSkeleton`
- `[./]python.[bat, sh] source/createSkeleton/createSkeleton.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- A 1 meter skinned mesh is created with an associated skeleton and animation under a SkelRoot called "skelRootGroup"
- Stage metadata is set at 24 timecodes per second, end timecode is set to 48 to make a 2 second animation

## Command Line Arguments

```
Usage:
  createSkeleton [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
