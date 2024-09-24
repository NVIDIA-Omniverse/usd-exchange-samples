# OpenUSD Exchange Samples: createStage

This sample demonstrates how to create/overwrite a stage with key metadata using the OpenUSD Exchange SDK and create cube and light prims.

## USD Modules
The Tf, Usd, UsdGeom, and UsdLux modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- getValidPrimName()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createStage`
- `[./]python.[bat, sh] source/createStage/createStage.py`

## Hardcoded items

- The stage is created with a Y-up axis, 1 cm linear units, default Scope prim named "World"
- A 1 meter cube named "cube" is created
- A distant light named "distantLight" is created

## Command Line Arguments

```
Usage:
  createStage [OPTION...]

  -a, --usda             Output a text stage rather than binary
  -h, --help             Print usage
  -p, --path arg         Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
