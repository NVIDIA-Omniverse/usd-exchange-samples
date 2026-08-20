# OpenUSD Exchange Samples: createCameras

This sample demonstrates how to open/create a stage with key metadata and create cameras using the OpenUSD Exchange SDK.

- Create a telephoto camera with a long lens and large aperture (narrow depth of field)
- Create a wide angle camera with a small aperture

## USD Modules

The Gf, Sdf, and Usd modules are used

## OpenUSD Exchange SDK functions

- createStage()
- defineCamera()
- getValidChildNames()
- saveStage()
- setLocalTransform()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createCameras`
- `python[3] source/python/createCameras.py`

## Hardcoded items

- If a stage is created, it has a default prim named "World", Z-up axis, 1 m linear units
- Create a telephoto camera with these properties:
    - A focal length of 100 mm
    - An fStop of 1.4
    - A focus distance of 88.62 m
    - A position of (65.72, -58.63, 14.16) m
    - An XYZ rotation of (81.47, -0.31, 47.48) degrees
- Create a wide-angle camera with these properties:
    - A focal length of 3.5 mm
    - An fStop of 32
    - A focus distance of 5.63 m
    - A position of (-5.07, -2.04, 3.05) m
    - An XYZ rotation of (53.98, 1.11, -45.36) degrees
- Focal length and aperture use tenths of a scene unit.
- Therefore, a 100 mm lens uses a focal length of 1 on this meter stage.
- Scale both values with the stage units to preserve the field of view and depth of field.

## Command Line Arguments

```
Usage:
  createCameras [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
  -z, --usdz          Package the output stage as USDZ
```
