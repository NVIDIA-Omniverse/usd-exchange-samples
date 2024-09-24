# OpenUSD Exchange Samples: createMesh

This sample demonstrates how to open/create a stage with key metadata and create cube mesh using the OpenUSD Exchange SDK.

Note that the `createCubeMesh()` functions are located inside the `source/common` folder because it will be used again.  Also note that it does more than just create a mesh, but for the sake of bite sized samples, focus on the Exchange SDK's `definePolyMesh()` function within the utility file.

## USD Modules

The Gf, Sdf, Usd, and UsdGeom modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- definePolyMesh()
- getValidChildNames()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createMesh`
- `[./]python.[bat, sh] source/createMesh/createMesh.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- A 1 meter mesh named "cubeMesh" is created at a height of 1.5 meters

## Command Line Arguments

```
Usage:
  createMesh [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
