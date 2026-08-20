# OpenUSD Exchange Samples: createCurves

This sample demonstrates how to open/create a stage with key metadata and create `UsdGeomBasisCurves` prims using the OpenUSD Exchange SDK.

- A [UsdGeomBasisCurves](https://openusd.org/release/api/class_usd_geom_basis_curves.html) prim can represent multiple batched curves that share the same basis and wrap settings.
- Curves authored with `widths` only are imaged as tubes; curves with both `widths` and `normals` are imaged as oriented ribbons.

Fourteen curve prims are authored in seven vertically stacked pairs (linear below, cubic above) to compare the same feature with different curve types:

- Batched multi-curve (two curves per prim, constant width)
- Constant width
- Per-vertex width
- Constant display color (with width)
- Per-vertex display color and opacity (with width)
- Oriented ribbon (indexed normals + constant width)
- Periodic wrap (closed loop)

## USD Modules

The Gf, UsdGeom, and Vt modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- defineXform()
- defineLinearBasisCurves()
- defineCubicBasisCurves()
- getValidChildName()
- getValidChildNames()
- saveStage()
- setLocalTransform()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createCurves`
- `python[3] source/python/createCurves.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Z-up axis, 1 m linear units
- A Xform prim named "curvesXform" is created under the default prim at a hardcoded world-space center of (-6.3, 9, 2); all curve prims are children of "curvesXform" with local transforms relative to that center
- Seven curve pairs are children of curvesXform with local X from -3.2 to 0.8 and local Y from -1 to 1; within each pair the linear curve is below (local Z = -1.1) and the cubic curve is above (local Z = 0.3, except periodic cubic at local Z = 1.1)
- Open single-curve prims use 7 control vertices; periodic wrap curves use 6 control vertices
- Batched prims pack two curves each: linear uses curveVertexCounts [7, 5] with 12 points; cubic uses [7, 4] with 11 points (bezier-valid counts)
- Constant width is 0.12 for most pairs; ribbon width is 0.16
- Per-vertex width values are 0.02, 0.04, 0.06, 0.08, 0.10, 0.14, and 0.16
- Constant display color is (1.0, 0.5, 0.2)
- Per-vertex display opacity values gradient from 1.0 to 0.0 across the seven control vertices
- Ribbon curves use a single indexed normal of (0, -1, 0) shared by all control vertices

## Command Line Arguments

```
Usage:
  createCurves [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
  -z, --usdz          Package the output stage as USDZ
```
