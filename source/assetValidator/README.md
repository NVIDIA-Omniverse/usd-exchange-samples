# OpenUSD Exchange Samples: Asset Validator

A command line USD validation tool (`omni_asset_validator.bat|sh`).

The Omniverse Asset Validator is a Python framework to provide `Usd.Stage` validation based on the [USD ComplianceChecker](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/pxr/usd/usdUtils/complianceChecker.py) (i.e. the same backend as the usdchecker commandline tool), with an aim to validate assets against Omniverse specific rules to ensure they run smoothly across all Omniverse products.

[Complete Asset Validator Documentation](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html)

To get the supported command line arguments, run `omni_asset_validator.bat|sh --help`. For example, the `--fix` flag will automatically apply fixes to a stage if possible (not all validation failures are automatically repairable):

```bash
omni_asset_validator.bat|sh --fix C:/USD/stage.usd
```

The `omni_asset_validator` script uses a bootstrap script, [assetValidatorBootstrap.py](./assetValidatorBootstrap.py), to aid in MDL material discovery. The bootstrap script adds the core MDL materials to the default search path so that paths like `OmniPBR.mdl` are not flagged as invalid by the Asset Validator.

The Asset Validator used by the `omni_asset_validator` script is installed by the USD Exchange Python Wheel. The script creates and activates a virtual environment for USD Exchange using [these directions from the SDK docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/getting-started.html#installation). To install the optional Asset Validator without using the wrapper or bootstrap script, use the optional/extra syntax as specified by the [USD Exchange Python Wheel Test Dependencies](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#python-wheel-optional-test-dependencies):

```bash
(usdex-env)> python -m pip install usd-exchange[test]
```

See the [USD Exchange Asset Validator docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#asset-validator) for more information on how to validate OpenUSD Stage/Layer data.
