# OpenUSD Exchange Samples: createMaterials

This sample demonstrates how to open/create a stage with key metadata, author several common material networks, and bind them to simple geometry using the OpenUSD Exchange SDK.

There are some key concepts that are demonstrated in this sample:
- A single material prim can contain shader networks for more than one render context. The sample shows RTX/MDL-oriented OmniPBR materials, OpenPBR/MaterialX materials, and USD Preview Surface materials.
- Material prims may contain inputs that connect to shader inputs, creating a "material interface".
    - Material interfaces give downstream tools a stable set of material-level controls.
- Texture helpers can set up the repeated wiring for common PBR maps such as color, normal, and ORM textures.
- Emissive helpers can author either a constant emissive color or a texture-driven emission.
- Glass helpers can author simple transmissive materials for USD Preview Surface, OpenPBR, and OmniPBR workflows.
- OmniPBR has UVW projection controls that can texture geometry without authored UVs. The textured USD Preview Surface and OpenPBR examples use regular texture coordinates.
- GeomSubsets can partition a mesh into face groups so each group can bind a different material. The sample creates a tablet mesh via `createMeshTabletExample()`, then uses `definePartitionedSubsets()` and `bindMaterialSubsets()` for front, body, and screen regions.

[Omniverse MDL Materials](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/materials.html)

[OpenPBR Surface Specification](https://academysoftwarefoundation.github.io/OpenPBR/) and [Material-X Node Index](https://kwokcb.github.io/MaterialX_Learn/documents/definitions/open_pbr_surface.html)

[OpenUSD Preview Surface Specification](https://openusd.org/release/spec_usdpreviewsurface.html)

## USD Modules

The Gf, Sdf, Usd, UsdGeom, UsdShade and UsdUtils modules are used.

## OpenUSD Exchange SDK functions

- addColorTextureToPbrMaterial()
- addEmissiveColorToPreviewMaterial()
- addEmissiveColorToPbrMaterial()
- addEmissiveTextureToPreviewMaterial()
- addEmissiveTextureToPbrMaterial()
- addOrmTextureToPbrMaterial()
- addNormalTextureToPbrMaterial()
- addColorTextureToPreviewMaterial()
- addNormalTextureToPreviewMaterial()
- addOrmTextureToPreviewMaterial()
- addPreviewMaterialInterface()
- bindMaterial()
- bindMaterialSubsets()
- createMdlShaderInput()
- defineGlassMaterial()
- defineGlassPbrMaterial()
- defineGlassPreviewMaterial()
- definePartitionedSubsets()
- definePbrMaterial()
- definePolyMesh()
- definePreviewMaterial()
- defineXform()
- getValidChildNames()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.

To run:

- `[./]run.[bat, sh] createMaterials`
- `python[3] source/python/createMaterials.py`

## What the sample creates

- If a stage is created, it will have a default prim named "World", Z-up axis, 1 m linear units
- Material and shader prims are created under a materials scope, typically named "Looks"
- The Fieldstone texture set is copied next to the output stage and reused by the material examples
- A translated `materialSampleGrid` Xform groups the meshes and spheres used to preview the materials
- The sample geometry is arranged as a small grid: textured mesh examples, glass spheres, a UVW projection sphere, compact emissive examples, and a mesh with GeomSubsets
- The textured PBR examples show the difference between:
    - `usdex.rtx.definePbrMaterial()`, which authors an RTX-oriented OmniPBR material with a USD Preview Surface fallback
    - `usdex.core.definePbrMaterial()`, which authors an OpenPBR/MaterialX material with a USD Preview Surface fallback
    - `usdex.core.definePreviewMaterial()`, which authors an USD Preview Surface material
- When `--usdz` is used, the sample skips the OmniPBR/MDL examples. USDZ packages are meant for portability, and MDL assets such as `@OmniPBR.mdl@` and `@OmniGlass.mdl@` are not portable.
- The UVW example binds an OmniPBR material to a sphere without UVs, then authors MDL inputs for world-space texture projection
- The Preview Surface example shows how to create a renderer-neutral material and add a material interface after the texture inputs are authored
- The glass examples bind red transmissive materials to spheres so the core differences between the material families are easy to compare
- The emissive examples show both color-driven and texture-driven emission on small stacked objects
- The mesh with GeomSubsets sits next to the glass examples and binds separate Preview Surface materials to its front, body, and screen face groups
- Spheres created by the shared utility include RTX refinement attributes (`refinementLevel` and `refinementEnableOverride`) so they display smoothly in RTX renderers

## Command Line Arguments

```
Usage:
  createMaterials [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
  -z, --usdz          Package the output stage as USDZ
```
