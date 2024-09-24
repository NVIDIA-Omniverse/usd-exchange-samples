# OpenUSD Exchange Samples: setDisplayNames

This sample demonstrates how to open/create a stage with key metadata and set prim display names using the OpenUSD Exchange SDK.

OpenUSD has strict requirements on what names are valid for a UsdObject. There is support for storing a "Display Name" as metadata on a Prim.

- [Exchange SDK documentation on display names](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/api/group__names.html)
- [OpenUSD documentation on UsdObject display names](https://openusd.org/release/api/class_usd_object.html#a89d396665875d4d4a88b5ecb0a22acb0)
- [OpenUSD GitHub PR for displayName metadata](https://github.com/PixarAnimationStudios/OpenUSD/pull/2055)

This sample introduces the `createCone()` and `createCylinder()` utilies for creating [UsdGeomGprims](https://openusd.org/release/api/usd_geom_page_front.html#UsdGeom_Gprim). They provide useful arguments, set extents (as required by these classes), and set custom Omniverse RTX refinement attributes.

This sample creates a multi-prim component rocket which users may wish to be selectable as a single object.  Many USD viewers support [model selection hierarchy](https://openusd.org/release/glossary.html#usdglossary-modelhierarchy) so the "rocket" Xform is assigned a [component](https://openusd.org/release/glossary.html#component) kind.

## USD Modules

The Gf, Sdf, Usd, and UsdGeom modules are used.

## OpenUSD Exchange SDK functions

- computeEffectiveDisplayName()
- createStage()
- getValidChildNames()
- get/setDisplayName()
- saveStage()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] setDisplayNames`
- `[./]python.[bat, sh] source/setDisplayNames/setDisplayNames.py`

## Hardcoded items

- Make a rocket with interesting part display names using 🚀

## Command Line Arguments

```
Usage:
  setDisplayNames [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
