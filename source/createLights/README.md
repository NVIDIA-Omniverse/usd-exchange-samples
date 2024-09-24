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
- `[./]python.[bat, sh] source/createLights/createLights.py`

## Hardcoded items

- If a stage is created, it will have a default prim named "World", Y-up axis, 1 cm linear units
- The rect light named "rectLight" is created with these properties:
    - 100x33 cm
    - 5,000 intensity
        - Note: this intensity is fairly high, the intention is to make a very visible blue light.  Also note that the default material in Omniverse Kit is very reflective so it's difficult to see the light on the `createStage` and `createMesh` geometry outside of the light's reflection.
        - Different DCC applications and renders will treat light intensity, exposure, etc. differently. When authoring lights, the target renderer and application should be considered.
    - 300 cm high, rotated to point down
- The dome light named "domeLight" is created with these properties:
    - 0.3 intensity
        - USDView likes a much lower intensity (0.3) than Omniverse Kit/RTX (1000). An intensity of 1000 washes out everything in USDView.
    - an HDRI texture is copied to the stage folder and set as the light texture file
    - to render properly in Omniverse Kit/RTX, apply a rotation -90 on the X axis to point -Z down
        - USDView correctly expects the [dome's top pole to be aligned with the world's +Y axis](https://openusd.org/dev/api/class_usd_lux_dome_light.html#details)

## Command Line Arguments

```
Usage:
  createLights [OPTION...]

  -a, --usda          Output a text stage rather than binary
  -h, --help          Print usage
  -p, --path arg      Alternate destination stage path (default: c:/Users/username/AppData/Local/Temp/usdex/sample.usdc)
```
