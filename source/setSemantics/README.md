# OpenUSD Exchange Samples: setSemantics

This sample demonstrates how to open/create a stage with key metadata and create prims with semantic labels. [The UsdSemantics library](https://openusd.org/release/api/usd_semantics_overview.html) provides semantic labeling of scenes within the OpenUSD framework. While prims already have a unique name and hierarchical identifier, it is sometimes useful to reason about the scene graph using a set of labels.

## USD Modules
The Gf, Sdf, Tf, UsdGeom, UsdSemantics modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- getValidPrimName()
- defineXform()
- setLocalTransform()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] setSemantics`
- `[./]python.[bat, sh] source/setSemantics/setSemantics.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- An Xform prim is created at location (300, 0, 300) to represent a house with Cube prims underneath that represent a wall, roof, door, and a window
- Q-Codes are applied to prims to show inherited semantics following codes gathered from https://www.wikidata.org/
  - /World/house ["Q3947"]
  - /World/house/wall ["Q3947", "Q42948"]
  - /World/house/roof ["Q3947", "Q83180"]
  - /World/house/door ["Q3947", "Q36794"]
  - /World/house/window ["Q3947", "Q35473"]
- A dense caption is set to the world default prim.

## Command Line Arguments

```
Usage:
  setSemantics [OPTION...]

  -a, --usda             Output a text stage rather than binary
  -h, --help             Print usage
  -s, --print-semantics  Print semantics
  -p, --path arg         Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
