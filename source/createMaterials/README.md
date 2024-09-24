# OpenUSD Exchange Samples: createMaterials

This sample demonstrates how to open/create a stage with key metadata and create material prims using the OpenUSD Exchange SDK.

There are some key concepts that are demonstrated in this sample:
- A single material prim can contain shader networks for more than one render context. In this sample, shaders are created for both the Material Definition Language (MDL) and the default (USD Preview Surface) render contexts.
- Material prims may contain inputs that connect to shader inputs, creating a "material interface".
    - Some renderers cannot access shader parameters and are required to use material inputs.
    - Some DCC tools and renderers do not support material interface inputs and require that all parameters be specified in shader prims.

[Omniverse MDL Materials](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/materials.html)

[OpenUSD Preview Surface Specification](https://openusd.org/release/spec_usdpreviewsurface.html)

## USD Modules

The Gf, Sdf, Usd, UsdGeom, UsdShade and UsdUtils modules are used.

## OpenUSD Exchange SDK functions

- addDiffuseTextureToPbrMaterial()
- addOrmTextureToPbrMaterial()
- addNormalTextureToPbrMaterial()
- bindMaterial()
- createStage()
- definePreviewMaterial()
- defineOmniPbrMaterial()
- definePolyMesh()
- getValidChildName()
- getValidChildNames()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createMaterials`
- `[./]python.[bat, sh] source/createMaterials/createMaterials.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- A 1 meter mesh with UVs named "pbrMesh" is created and an OmniPBR/Preview Surface material is bound to it
    - Material and shader prims are created under a scope prim typically named "Looks"
- A 1 meter sphere with no UVs named "pbrSphere" is created and an OmniPBR/Preview Surface material is bound to it
    - OmniPBR has UV world projection parameters that allow shapes and meshes with no UVs to be textured
    - There is no mechanism for UV world projection with USD Preview Surface, so that material may not look correct on the UV-less sphere
- A 1 meter mesh with UVs named "previewSurfaceMesh" is created with a USD Preview Surface material
    - Material and shader prims are created under a scope prim typically named "Looks"

## Command Line Arguments

```
Usage:
  createMaterials [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
