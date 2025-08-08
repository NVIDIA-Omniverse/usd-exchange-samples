# OpenUSD Exchange Samples: createAsset

This sample demonstrates how to open/create a stage with key metadata and create an asset that follows the Atomic Component asset structure using the OpenUSD Exchange SDK.

This sample follows NVIDIA's
[Principles of Scalable Asset Structure](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html).

An asset is a named, versioned, and structured container of one or more resources which may include composable OpenUSD layers, textures,
volumetric data, and more.

Atomic models are entirely self contained, have no external dependencies, and are usually
[Components](https://openusd.org/release/glossary.html?highlight=kind#usdglossary-component) in the
[Model Hierarchy](https://openusd.org/release/glossary.html?highlight=kind#usdglossary-modelhierarchy).

## USD Modules

The Gf, Sdf, Usd, UsdGeom, UsdShade, and Kind modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- saveStage()
- defineReference()
- defineXform()
- definePreviewMaterial()
- createAssetPayload()
- addAssetLibrary()
- addAssetContent()
- addAssetInterface()
- bindMaterial()
- setLocalTransform()
- setDisplayName()
- getGeometryToken()
- getMaterialsToken()
- getValidChildNames()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createAsset`
- `[./]python.[bat, sh] source/createAsset/createAsset.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- A new flower atomic component asset is created then payloaded into the stage

## Command Line Arguments

```
Usage:
  createAsset [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
