# OpenUSD Exchange Samples: createAssembly
This sample demonstrates how to open/create a stage with key metadata and configure an assembly hierarchy using the OpenUSD Exchange SDK.

This sample follows NVIDIA's [USD Assemblies for Data Aggregation Guide](https://docs.omniverse.nvidia.com/dang/latest/guide/usd/usd-assemblies.html)

Assemblies are used in the [Model Hierarchy](https://openusd.org/release/glossary.html?highlight=kind#usdglossary-modelhierarchy) and are annotated
with the “assembly” kind to make it easy to identify assembly hierarchies. The referenced prims within assemblies may either
be assemblies themselves (e.g., playground within a park), or they may be “component models” with kind = “component” (e.g., slide within a playground).

## USD Modules

The Gf, Sdf, Usd, UsdGeom, UsdShade, and Kind modules are used.

## OpenUSD Exchange SDK functions

- createStage()
- saveStage()
- defineReference()
- defineXform()
- definePreviewMaterial()
- addPrimvarShaderToPreviewMaterial()
- bindMaterial()
- createConstantPrimvar()
- setConstantPrimvar()
- createAssetPayload()
- addAssetLibrary()
- addAssetContent()
- addAssetInterface()
- configureAssemblyHierarchy()
- setLocalTransform()
- getGeometryToken()
- getMaterialsToken()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createAssembly`
- `python[3] source/python/createAssembly.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Z-up axis, 1 m linear units
- New Pinewood derby car and track atomic component assets are created
    - The car assets have a "bodyPaintColor" [primvar](https://openusd.org/release/api/class_usd_geom_primvar.html#details) as a form of [asset parameterization](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html#asset-parameterization). The sample creates it with the scalar Color3f type, and OpenUSD Exchange SDK authors the required array-valued constant primvar.
- A Pinewood derby race "assembly" is setup using the track and two cars (one blue, one green) as "components"

## Command Line Arguments

```
Usage:
  createAssembly [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
  -z, --usdz          Package the output stage as USDZ
```
