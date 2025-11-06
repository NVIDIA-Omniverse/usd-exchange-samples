2.1.0
-----
Release: November 2025

OpenUSD Exchange SDK v2.1.0

* Samples
    * The Python samples use the USD Exchange Python Wheel instead of the runtime dependencies installed from the `install_usdex` script
        * [The OpenUSD Exchange Wheel](https://pypi.org/project/usd-exchange/)
        * The Python samples should now be run within a virtual environment, see [How to Build and Run Samples](./README.md#how-to-build-and-run-samples)
    * The samples now use the USD Exchange SDK's gprim functions to create spheres, cubes, planes, and cones
    * Added [createAssembly](./source/createAssembly/README.md) to demonstrate how to configure an assembly hierarchy using the USD Exchange SDK
    * Demonstrate the usage of custom attributes more clearly in [createMaterials](./source/createMaterials/README.md)
    * Pull some of the per-sample test code into the BaseTestCase class
    * Add some documentation about `UsdGeomXformCache` in the [createTransforms README](./source/createTransforms/README.md)

* Dependencies
    * OpenUSD [v25.05](https://github.com/PixarAnimationStudios/OpenUSD/blob/v25.05/CHANGELOG.md)
    * OpenUSD Exchange SDK [v2.1.0](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
    * Omniverse Asset Validator [v1.4.2](https://docs.omniverse.nvidia.com/kit/docs/asset-validator)

2.0.1
-----
Release: August 2025

OpenUSD Exchange SDK v2.0.1

* Dependencies
    * OpenUSD [v25.05](https://github.com/PixarAnimationStudios/OpenUSD/blob/v25.05/CHANGELOG.md)
    * OpenUSD Exchange SDK [v2.0.1](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
    * Omniverse Asset Validator [v1.1.6](https://docs.omniverse.nvidia.com/kit/docs/asset-validator)

2.0.0
-----
Release: August 2025

OpenUSD Exchange SDK v2.0.0

* Samples
    * Switch to USD 25.05
    * Add an "all" argument to `run.bat|sh` and `python.bat|sh` to run all of the samples in proper order
    * Add new samples
        * [Asset Structure](./source/createAsset/README.md)
        * [Physics](./source/createPhysics/README.md)
        * [Semantics](./source/setSemantics/README.md)
* Dependencies
    * OpenUSD [v25.05](https://github.com/PixarAnimationStudios/OpenUSD/blob/v25.05/CHANGELOG.md)
    * OpenUSD Exchange SDK [v2.0.0](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
    * Omniverse Asset Validator [v1.1.6](https://docs.omniverse.nvidia.com/kit/docs/asset-validator)

1.1.0
-----
Release: April 2025

OpenUSD Exchange SDK v1.1.0

* Samples
    * Support USD 24.11+ in the usdTraverse Makefile
* usdview.sh|bat
    * Initialize virtual environment with usdview runtime requirements
* Dependencies
    * OpenUSD [v24.08](https://github.com/PixarAnimationStudios/OpenUSD/blob/v24.08/CHANGELOG.md)
    * OpenUSD Exchange SDK [v1.1.0](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
    * Omniverse Asset Validator [v0.16.2](https://docs.omniverse.nvidia.com/kit/docs/asset-validator)
    * Omniverse Transcoding [v1.0.0](https://docs.omniverse.nvidia.com/kit/docs/omni-transcoding)

1.0.0
-----
Release: October 2024

OpenUSD Exchange SDK v1.0.0

* Samples
    * The Connect Samples were reorganized to make them more digestible and switched to the Exchange SDK to focus on OpenUSD topics.
* Dependencies
    * OpenUSD [v24.08](https://github.com/PixarAnimationStudios/OpenUSD/blob/v24.08/CHANGELOG.md)
    * OpenUSD Exchange SDK [v1.0.0](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
    * Omniverse Asset Validator [v0.14.2](https://docs.omniverse.nvidia.com/kit/docs/asset-validator)
    * Omniverse Transcoding [v1.0.0](https://docs.omniverse.nvidia.com/kit/docs/omni-transcoding)
