# OpenUSD Exchange Samples: createReferences

This sample demonstrates how to open/create a stage with key metadata and create a reference and payload using the OpenUSD Exchange SDK.

[References](https://openusd.org/release/glossary.html#usdglossary-references) are primarily used to compose smaller units of scene description into larger scenes.  [Payloads](https://openusd.org/release/glossary.html#usdglossary-payload) are a special kind of Reference that can be unloaded. [Overs](https://openusd.org/release/glossary.html#usdglossary-over) may be applied to these reference prims to override attributes.

When creating the component stage the sample uses a pattern that's different than simply creating a stage on disk and modifying it. The `createComponentStage()` function intentionally creates a new stage in memory, sets key metadata, adds prims to it, then exports it using OpenUSD Exchange's `exportLayer()` function.  This is useful when generating USD data to prevent invalid or incomplete USD files on disk in the case of a failure.

- `UsdStage::CreateInMemory()`
- `usdex::core::configureStage()`
- `usdex::core::exportLayer()`

This sample abuses mesh duplication by creating 8 mesh cubes in the component stage. A future optimization could use internal references or even scenegraph instances.

## USD Modules

The Gf, Sdf, Usd, and UsdGeom modules are used.

## OpenUSD Exchange SDK functions

- configureStage()
- createStage()
- defineXform()
- exportLayer()
- getValidChildNames()
- saveStage()
- Vec3fPrimvarData()
- defineReference()
- definePayload()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createReferences`
- `[./]python.[bat, sh] source/createReferences/createReferences.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- A new "component" stage is created that represents a prop, or component.  It contains a 2x2x2 grouping of mesh cubes
- The new "component" stage is then used in separate reference and payload prim
- The reference prim gets a scale override on the last mesh prim in the component
- The payload prim gets a display color override on the last mesh prim in the component

## Command Line Arguments

```
Usage:
  createReferences [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
