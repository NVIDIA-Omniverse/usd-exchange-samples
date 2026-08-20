# OpenUSD Exchange Samples: createLights

This sample demonstrates how to open/create a stage with key metadata and create OpenUSD lights using the OpenUSD Exchange SDK.

- A [UsdLuxRectLight](https://openusd.org/release/api/class_usd_lux_rect_light.html#details) describes light emitted from one side of a rectangle.
- A [UsdLuxDomeLight](https://openusd.org/release/api/class_usd_lux_dome_light.html#details) describes light emitted inward from a distant external environment, such as a sky or imaged base light.

## USD Modules

The Gf, Sdf, Usd, and UsdLux modules are used.

## OpenUSD Exchange SDK functions

- createColorAttr()
- createStage()
- defineDomeLight()
- defineRectLight()
- getValidChildNames()
- saveStage()
- setLocalTransform()

## Languages

This sample is implemented in both C++ and Python.  To run:

- `[./]run.[bat, sh] createLights`
- `python[3] source/python/createLights.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Z-up axis, 1 m linear units
- The rect light named "rectLight" is created with these properties:
    - A width and height of 0.25 m
    - An intensity of 500
    - A color value of (0.3, 0, 1)
    - A position of (0, 0, 0.6) m
    - A downward direction along the local -Z axis
    - Different applications and renderers can interpret light properties differently. Consider the target application and renderer when you author a light.
- The dome light named "domeLight" is created with these properties:
    - 0.3 intensity
        - USDView likes a much lower intensity (0.3) than Omniverse Kit/RTX (1000). An intensity of 1000 washes out everything in USDView.
    - an HDRI texture is copied to the stage folder and set as the light texture file
    - a 90-degree X-axis rotation aligns the dome's +Y top pole with the stage's +Z up-axis
        - Omniverse Kit/RTX does not currently render this authored DomeLight rotation correctly
        - Kit/RTX treats the DomeLight environment as Z-up, unlike the OpenUSD +Y pole convention
    - a 1,000 m guide radius preserves the previous 1 km guide size after the stage-unit conversion

## Command Line Arguments

```
Usage:
  createLights [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
  -z, --usdz          Package the output stage as USDZ
```
