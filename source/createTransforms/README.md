# OpenUSD Exchange Samples: createTransforms

This sample demonstrates how to open/create a stage with key metadata and apply transforms to prims using the OpenUSD Exchange SDK.

- Find or create a [UsdGeomXformable](https://openusd.org/dev/api/class_usd_geom_xformable.html#details) https://openusd.org/dev/api/class_usd_geom_cube.html#details, read its tranform and rotate it 45 degrees on the stage's up-axis.
- Create a [UsdGeomXform](https://openusd.org/dev/api/class_usd_geom_xform.html#details) prim and adjust its translation
- Create a [UsdGeomCube](https://openusd.org/dev/api/class_usd_geom_cube.html#details) prim as a child of the Xform prim and adjust its scale to make a floor

## USD Modules

The Gf, Sdf, and Usd modules are used

## OpenUSD Exchange SDK functions

- createStage()
- defineXform()
- getLocalTransform()
- getLocalTransformComponents()
- getValidChildNames()
- saveStage()
- setLocalTransform()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createTransforms`
- `[./]python.[bat, sh] source/createTransforms/createTransforms.py`

## Hardcoded items

- If a stage is created, it has a default prim named "World", Y-up axis, 1 cm linear units
- A prim (either found or created) is rotated 45 degrees in the prim's middle rotation axis
    - The prim is found using a method called [stage traversal](https://openusd.org/release/tut_traversing_stage.html)
    - If a xformable prim isn't found a cube will be created to rotate
    - Note that the typical rotation order is XYZ, so the expectation is that the sample rotates the prim on the Y axis
- A Xform prim named "groundXform" is created and lowered 55 cm
- A cube prim named "groundCube" is created as a child of "groundXform" with a scale of (20, 0.1, 20)

## Command Line Arguments

```
Usage:
  createTransforms [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
