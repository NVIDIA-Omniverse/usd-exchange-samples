# Contributing to the OpenUSD Exchange Samples

If you are interested in contributing to the OpenUSD Exchange Samples, your contributions will fall
into three categories:
1. You want to report a bug, feature request, or documentation issue
2. You want to implement a feature or bug-fix for an outstanding issue
3. You want to propose a new Feature and implement it

In all cases, first search the existing [GitHub Issues](https://github.com/NVIDIA-Omniverse/usd-exchange-samples/issues) to see if anyone has reported something similar.

If not, create a new [GitHub Issue](https://github.com/NVIDIA-Omniverse/usd-exchange-samples/issues/new/choose) describing what you encountered or what you want to see changed.

Whether adding details to an existing issue or creating a new one, please let us know what companies are impacted.

## Code contributions

We are not currently accepting direct code contributions to the OpenUSD Exchange Samples. If you have feedback that is best explained in code, feel free to fork the repository on GitHub, create a branch demonstrating your intent, and either link it to a GitHub Issue or open a Pull Request back upstream.

We will not merge any GitHub Pull Requests directly, but we will take the suggestion under advisement and discuss internally. If you require attribution for such code, should it be adopted internally, please be sure that both your own legal team & NVIDIA legal team finds this acceptable prior to suggesting the changes. The Contributor License Agreement for this project is located in [CLA.md](CLA.md).

If you want to implement a feature, or change the logic of existing features, you are welcome to modify the code on a personal clone/mirror/fork & re-build the libraries from source. See [Building](#building) for more details.


## Building

To build the samples yourself, use `build.bat` or `build.sh`, depending on your local platform.

The build script assembles the OpenUSD Exchange SDK + OpenUSD runtime (via `install_usdex`) and then compiles the C++ samples with CMake, consuming the SDK through `find_package(usd-exchange)`. Pass `-d`/`--debug` for a debug build. See [CMakeLists.txt](./CMakeLists.txt) to learn how the samples are compiled and linked.

If the required Python packages are hosted on an additional package index, set `USDEX_PYPI_EXTRA_INDEX_URL` before building, testing, or running `validate_usd`. The samples translate this USD Exchange-specific setting to the native pip and uv environment variables used by each workflow. Explicit `PIP_EXTRA_INDEX_URL` or `UV_EXTRA_INDEX_URL` values take precedence for their respective installer.


## Testing

To run all of the sample tests, use `repo test`. The tests run in a single `main` suite, which contains all of the sample tests and is run within a virtual environment.

To run only certain sample tests the test scripts must be run directly. For instance, the following command will reuse the existing test virtual environment and run just the `createAsset` tests, run:

```
Linux:
tools/wheel/test.sh --reuse -k testCreateAsset

Windows:
tools\wheel\test.bat --reuse -k testCreateAsset
```

See `python -m unittest --help` for more information on test options.

These arguments to reuse the virtual test environment and filter tests are also supported within [repo.toml](./repo.toml). To achieve the same result as above, add this to the `[repo_test.suites.main]` section:

```toml
[repo_test.suites.main]
args = ["--reuse", "-k", "testCreateAsset"]
```

## Adding a sample

The samples are intended to be small and concise, demonstrating one key concept from the OpenUSD or OpenUSD Exchange SDK at a time.

### New stage or existing stage

There are two stage origination methods: "create/overwrite" and "open/create". [createStage](./source/createStage) is the only sample that uses the "create/overwrite" method because it's intended to be the first sample studied and run. It will always create a new stage or overwrite the existing `sample.usd[a,c]` file. All the other stages "open/create" this sample stage, attempting first to open it and append their key concept prims.  They will only create a new stage if it doesn't already exist.

### Samples expand upon each other

When a sample opens an existing stage and adds prims, these new prims should be placed in a location that works with all the other samples' prims. There is a test that runs all of the samples in succession called [testRunAll](./source/tests/testRunAll.py). To execute this test and keep the output stage see the [README directions](./README.md#running-all-samples-together).

### Samples have tests

All samples should have a Python [unittest](https://docs.python.org/3/library/unittest.html) located under the [source/tests](./source/tests) folder. There is a lot of boilerplate code in these tests, but the emphasis is to ensure that all of the command line arguments work properly and the output stage contains valid and correct prims.

### Programing language

Because the OpenUSD and OpenUSD Exchange SDKs both provide Python bindings, each sample should be written in C++ and Python. If the situation merits it, a single language implementation could suffice. The C++ implementation resides in the sample's directory (eg. `source/createThing/createThing.cpp`) while the Python implementation resides in the project's python directory (`source/python/createThing.py`).

### Sample name lists

For the samples to build, run, and test properly they are explicitly listed in the [allSamples.txt](./allSamples.txt) file. A link to the new sample's README.md file should be added to the [Samples for the OpenUSD Exchange SDK](./README.md#samples-for-the-openusd-exchange-sdk) section.
