# OpenUSD Exchange Samples: Asset Validator

A command line USD validation tool (`omni_asset_validator.bat|sh`).

The Omniverse Asset Validator is a Python framework to provide `Usd.Stage` validation based on the [USD ComplianceChecker](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/pxr/usd/usdUtils/complianceChecker.py) (i.e. the same backend as the usdchecker commandline tool), with an aim to validate assets against Omniverse specific rules to ensure they run smoothly across all Omniverse products.

[Complete Asset Validator Documentation](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html)

To get the supported command line arguments, run `omni_asset_validator.bat|sh --help`. For example, the `--fix` flag will automatically apply fixes to a stage if possible (not all validation failures are automatically repairable):

```bash
omni_asset_validator.bat|sh --fix C:/USD/stage.usd
```
