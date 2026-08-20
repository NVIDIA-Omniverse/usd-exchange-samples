# OpenUSD Exchange Samples: USD Validation

A command line USD validation tool (`validate_usd.bat|sh`).

The `usd-validation-nvidia` package provides `Usd.Stage` validation based on the [OpenUSD Validation framework](https://openusd.org/release/api/md_pxr_usd_validation_usd_validation__r_e_a_d_m_e.html). This framework extends validation capabilities with additional rules and provides automatic issue fixing.

[`usd-validation-nvidia` repository](https://github.com/NVIDIA-Omniverse/usd-validation-nvidia/tree/main)

To get the supported command line arguments, run `validate_usd.bat|sh --help`. For example, the `--fix` flag will automatically apply fixes to a stage if possible (not all validation failures are automatically repairable):

```bash
validate_usd.bat|sh --fix C:/USD/stage.usd
```

The `validate_usd` script uses a bootstrap script, [validateUsdBootstrap.py](./validateUsdBootstrap.py), to aid in MDL material discovery. The bootstrap script adds the core MDL materials to the default search path so that paths like `OmniPBR.mdl` are not flagged as invalid by the `usd-validation-nvidia` package. There is a `nvidia_usd_validate` executable in the Python wheel if there's no need for MDL material path handling.

The `usd-validation-nvidia` package used by the `validate_usd` script is installed by the USD Exchange Python Wheel. The script creates and activates a virtual environment for USD Exchange using [these directions from the SDK docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/getting-started.html#installation). To install `usd-validation-nvidia` without using the wrapper or bootstrap script, use the optional/extra syntax as specified by the [USD Exchange Python Wheel Test Dependencies](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#python-wheel-optional-test-dependencies):

```bash
(usdex-env)> python -m pip install usd-exchange[test]
```

See the [USD Exchange Validation docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#asset-validator) for more information on how to validate OpenUSD Stage/Layer data.
