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
- `[./]python.[bat, sh] source/createCameras/createCameras.py`

## Hardcoded items

- If a stage is created, it has a default prim named "World", Y-up axis, 1 cm linear units
- Create a camera with a focal length of 100 mm with an fStop of 1.4 20 m from the origin of the stage
- Create a camera with a focal length of 3.5 mm with an fStop of 32 about 2.5 m from the origin of the stage

## Command Line Arguments

```
Usage:
  createCameras [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
