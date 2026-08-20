# Samples for the OpenUSD Exchange SDK

These samples demonstrate some key concepts for writing OpenUSD converters. The samples use OpenUSD and the OpenUSD Exchange SDK ([docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/index.html), [github](https://github.com/NVIDIA-Omniverse/usd-exchange)) to demonstrate how to author consistent and correct USD:

- [`USD Validation`](./source/validateUsd/README.md)
- [`createStage`](./source/createStage/README.md)
- [`createTransforms`](./source/createTransforms/README.md)
- [`createMesh`](./source/createMesh/README.md)
- [`createCurves`](./source/createCurves/README.md)
- [`createMaterials`](./source/createMaterials/README.md)
- [`createReferences`](./source/createReferences/README.md)
- [`createAsset`](./source/createAsset/README.md)
- [`createCameras`](./source/createCameras/README.md)
- [`createLights`](./source/createLights/README.md)
- [`createPhysics`](./source/createPhysics/README.md)
- [`createSkeleton`](./source/createSkeleton/README.md)
- [`setDisplayNames`](./source/setDisplayNames/README.md)
- [`setSemantics`](./source/setSemantics/README.md)

## How to Build and Run Samples

### Linux
This project builds with CMake and requires "make" and "g++". The build script fetches a pinned CMake automatically (or uses a system `cmake` if one is present), so you only need "make" and "g++" installed:

- Open a terminal.
- To obtain "make" type `sudo apt install make` (Ubuntu/Debian), or `yum install make` (CentOS/RHEL).
- For "g++" type `sudo apt install g++` (Ubuntu/Debian), or `yum install gcc-c++` (CentOS/RHEL).

Use the provided build script to assemble the OpenUSD Exchange SDK + OpenUSD runtime (via `install_usdex`) and compile the C++ samples with CMake. The samples consume the SDK through `find_package(usd-exchange)`.

```bash
./build.sh
```

For debug builds, use `./build.sh -d`

#### C++ Samples

Use the `run.sh` script (e.g. `./run.sh createStage`) to execute each program with a pre-configured environment.

> Tip: If you prefer to manage the environment yourself, add `<samplesRoot>/_install/linux-x86_64/release/lib` to your `LD_LIBRARY_PATH`.

For command line argument help, use `--help`
```bash
./run.sh createStage --help
```

You can also [run all samples together](#running-all-samples-together), saved into a single layer.

#### USDZ Output

Samples can package their output stage as USDZ by passing `--usdz`. The sample still writes its normal USD stage first, then creates an independent `.usdz` package next to that stage using the same filename stem:

```bash
./run.sh createMesh -p /tmp/sample.usdc --usdz
```

The `--path` argument remains the writable USD stage path. Passing a `.usdz` path to `--path` is not supported because USDZ packages are not writable stage layers.

USDZ packaging requires every external asset dependency to resolve on disk. When `createMaterials` is run with `--usdz`, it skips the OmniPBR/MDL-specific examples so the package contains only dependencies that can be localized without MDL search-path configuration.

#### Python Samples (with a virtual environment and the USD Exchange wheel)

Setup and activate a virtual environment for USD Exchange using [these directions from the SDK docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/getting-started.html#installation).

To install the optional `usd-validation-nvidia` package, use the optional/extra syntax:

```bash
(usdex-env): python3 -m pip install usd-exchange[test]
```

Call `python3` directly (e.g. `python3 source/python/createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
(usdex-env): python3 source/python/createStage.py --help
```

### Windows
#### Building
This project requires Microsoft Visual Studio 2022 or newer. Download & install [Visual Studio with C++](https://visualstudio.microsoft.com/vs/features/cplusplus). The build script fetches a pinned CMake automatically (or uses a system `cmake` if one is present), so Visual Studio (compiler + MSBuild) is the only manual install.

Use the provided build script to assemble the OpenUSD Exchange SDK + OpenUSD runtime (via `install_usdex`) and compile the C++ samples with CMake. The samples consume the SDK through `find_package(usd-exchange)`.
```bash
.\build.bat
```

For debug builds, use `.\build.bat -d`

#### C++ Samples

Use the `run.bat` script (e.g. `.\run.bat createStage`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\run.bat createStage --help
```

You can also [run all samples together](#running-all-samples-together), saved into a single layer.

#### Python Samples (with a virtual environment and the USD Exchange wheel)

Setup and activate a virtual environment for USD Exchange using [these directions from the SDK docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/getting-started.html#installation).

To install the optional `usd-validation-nvidia` package, use the optional/extra syntax:

```bash
(usdex-env)> python.exe -m pip install usd-exchange[test]
```

Call `python.exe` directly (e.g. `python.exe source/python/createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
(usdex-env)> python.exe source/python/createStage.py --help
```

#### Building within the Visual Studio IDE

CMake generates a Visual Studio solution under `_build/cmake/windows-x86_64/release` (run `.\build.bat` once to produce it). Open `usd-exchange-samples.sln` from that folder in Visual Studio to tweak, debug, and rebuild the sample C++ code.

> Note : If the user installs the OpenUSD Exchange Samples into the `%LOCALAPPDATA%` folder, Visual Studio will not "Build" properly when changes are made because there is something wrong with picking up source changes.  Do one of these things to address the issue:
>  - `Rebuild` the project with every source change rather than `Build`
>  - Copy the OpenUSD Exchange Samples folder into another folder outside of `%LOCALAPPDATA%`
>  - Make a junction to a folder outside of %LOCALAPPDATA% and open the solution from there:
>    - `mklink /J C:\usd-exchange-samples %LOCALAPPDATA%\cloned-repos\usd-exchange-samples`


#### Issues with Self-Signed Certs
If the scripts from the Samples fail due to self-signed cert issues, a possible workaround would be to do this:

Install python-certifi-win32 which allows the windows certificate store to be used for TLS/SSL requests:

```bash
tools\packman\python.bat -m pip install python-certifi-win32 --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### Running All Samples Together

The samples are intended to be run sequentially and will build up the USD stage that is originally created in the [`createStage`](./source/createStage/README.md) sample.  The can also be run independently and will either open or create a stage depending on whether it exists.  To run all of the samples sequentially with one command, type this in the command line after building:

```
Linux:
./run.sh all
python3 source/python/all.py

Windows:
.\run.bat all
python.exe source\python\all.py
```

This will output a single layer file after all of the samples have run sequentially. The output is a standard USD stage that can be opened in any USD viewer.

### Build and CI/CD Tools
The Samples build with plain CMake, consuming the OpenUSD Exchange SDK through `find_package(usd-exchange)`. The [Repo Tools Framework (`repo_man`)](https://docs.omniverse.nvidia.com/kit/docs/repo_man) and packman are still used to fetch the SDK package (and its OpenUSD), to run `install_usdex`, and for testing/formatting/CI. This is a representative setup for how a customer's CMake application would link against OpenUSD and the OpenUSD Exchange SDK. Here's a list of interesting files:

- [CMakeLists.txt](./CMakeLists.txt) - the CMake build for the samples; calls `find_package(usd-exchange)` and links each sample
- [build.sh](./build.sh) / [build.bat](./build.bat) - assemble the SDK + OpenUSD runtime via `install_usdex`, then configure + build with CMake
- `_build/target-deps/usd-exchange/release/lib/cmake/usd-exchange/` - the SDK's CMake package config (provides the `usdex::core` / `usdex::rtx` targets and the `usdex_target_link_usd()` helper)
  - this is not available until dependencies are fetched

For details on choosing and installing the OpenUSD Exchange SDK build flavors, features, or versions, see the [install_usdex](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#install-usdex) tool documentation.

## Using the OpenUSD Exchange SDK in an Application

See the [OpenUSD Exchange SDK Native Application Guide](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/native-application.html) for a walkthrough of how use the OpenUSD Exchange SDK and OpenUSD in a native application.

## External Support

First search the existing [GitHub Issues](https://github.com/NVIDIA-Omniverse/usd-exchange-samples/issues) and the [OpenUSD Exchange SDK Discussions](https://github.com/NVIDIA-Omniverse/usd-exchange/discussions) to see if anyone has reported something similar.

If not, create a new [GitHub Issue](https://github.com/NVIDIA-Omniverse/usd-exchange-samples/issues/new) or forum topic explaining your bug or feature request.

- For bugs, please provide clear steps to reproduce the issue, including example failure data as needed.
- For features, please provide user stories and persona details (i.e. who does this feature help and how does it help them).

Whether adding details to an existing issue or creating a new one, please let us know what companies are impacted.


## Licenses

The license for the samples is located in [LICENSE.md](./LICENSE.md).

Third party license notices for dependencies used by the samples are located in the [OpenUSD Exchange SDK License Notices](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/licenses.html).

## Documentation and learning resources for USD and Omniverse

[OpenUSD Docs - Creating Your First USD Stage](https://openusd.org/docs/Hello-World---Creating-Your-First-USD-Stage.html)

[OpenUSD API Docs](https://openusd.org/docs/api/index.html)

[OpenUSD User Docs](https://openusd.org/release/index.html)

[NVIDIA OpenUSD Resources and Learning](https://developer.nvidia.com/usd)

[OpenUSD Code Samples Documentation](https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/usd.html)

[OpenUSD Code Samples Repository](https://github.com/NVIDIA-Omniverse/OpenUSD-Code-Samples)

[NVIDIA OpenUSD Docs](https://developer.nvidia.com/usd)

[NVIDIA OpenUSD Exchange SDK Docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
