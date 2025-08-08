# Samples for the OpenUSD Exchange SDK

These samples demonstrate some key concepts for writing OpenUSD converters. The samples use OpenUSD and the OpenUSD Exchange SDK ([docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/index.html), [github](https://github.com/NVIDIA-Omniverse/usd-exchange)) to demonstrate how to author consistent and correct USD:

- [`Asset Validator`](./source/assetValidator/README.md)
- [`createStage`](./source/createStage/README.md)
- [`createTransforms`](./source/createTransforms/README.md)
- [`createMesh`](./source/createMesh/README.md)
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
This project requires "make" and "g++".

- Open a terminal.
- To obtain "make" type `sudo apt install make` (Ubuntu/Debian), or `yum install make` (CentOS/RHEL).
- For "g++" type `sudo apt install g++` (Ubuntu/Debian), or `yum install gcc-c++` (CentOS/RHEL).

Use the provided build script to download all other dependencies (e.g USD), create the Makefiles, and compile the code.

```bash
./repo.sh build
```

For debug builds, use `./repo.sh build -d`

#### C++ Samples

Use the `run.sh` script (e.g. `./run.sh createStage`) to execute each program with a pre-configured environment.

> Tip: If you prefer to manage the environment yourself, add `<samplesRoot>/_build/linux64-x86_64/release` to your `LD_LIBRARY_PATH`.

For command line argument help, use `--help`
```bash
./run.sh createStage --help
```

You can also [run all samples together](#running-all-samples-together), saved into a single layer.

#### Python Samples

Use the `python.sh` script (e.g. `./python.sh source/createStage/createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`
```bash
./python.sh source/createStage/createStage.py --help
```

### Windows
#### Building
This project requires Microsoft Visual Studio 2019 or newer. Download & install [Visual Studio with C++](https://visualstudio.microsoft.com/vs/features/cplusplus).

Use the provided build script to download all dependencies (e.g USD), create the projects, and compile the code.
```bash
.\repo.bat build
```

For debug builds, use `.\repo.bat build -d`

#### C++ Samples

Use the `run.bat` script (e.g. `.\run.bat createStage`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\run.bat createStage --help
```

You can also [run all samples together](#running-all-samples-together), saved into a single layer.

#### Python Samples

Use the `python.bat` script (e.g. `.\python.bat source\createStage\createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\python.bat source\createStage\createStage.py --help
```

#### Building within the Visual Studio IDE

To build within the VS IDE, open the solution found in the `_compiler` folder in Visual Studio.  The sample C++ code can then be tweaked, debugged, rebuilt, etc. from there.

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
./python.sh all

Windows:
.\run.bat all
.\python.bat all
```

This will output a single layer file after all of the samples have run sequentially. This output layer can be passed as the first command line argument to the `usdview.[bat|sh]` script to view it.

#### Run the C++ and Python Samples

The unittests have a similar process, but run both C++ and Python Samples:

```
Linux:
./repo.sh test -f testRunAll -e keep

Windows:
.\repo.bat test -f testRunAll -e keep
```

### Build and CI/CD Tools
The Samples repository uses the [Repo Tools Framework (`repo_man`)](https://docs.omniverse.nvidia.com/kit/docs/repo_man) to configure premake, packman, build and runtime dependencies, testing, formatting, and other tools. Packman is used as a dependency manager for packages like OpenUSD, the Omniverse Asset Validator, the OpenUSD Exchange SDK, and other items. The Samples use OpenUSD Exchange SDK's repo_man, premake, and packman tooling as templates for including and linking against OpenUSD, the OpenUSD Exchange SDK, and other dependencies.  These can serve as an example for the build and runtime configuration that a customer's application might require.  Here's a list of interesting files:

- [premake5.lua](./premake5.lua) - the build configuration file for the samples
- [prebuild.toml](./prebuild.toml) - consumed by the repo build tools to specify where runtime dependencies should be copied (beyond what `repo install_usdex` already installs)
- `_build/target-deps/usd-exchange/release/dev/tools/premake/usdex_build.lua` - the OpenUSD Exchange SDK's premake build configuration template file for including USD, the OpenUSD Exchange SDK itself, and other libraries.
  - this file isn't available until dependencies are fetched

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

[OpenUSD Code Samples](https://github.com/NVIDIA-Omniverse/OpenUSD-Code-Samples)

[NVIDIA OpenUSD Docs](https://developer.nvidia.com/usd)

[NVIDIA OpenUSD Exchange SDK Docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
