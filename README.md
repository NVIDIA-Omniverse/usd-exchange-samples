# OpenUSD Exchange Samples for the OpenUSD Exchange SDK

These samples demonstrate some key concepts for writing OpenUSD converters. The samples use the OpenUSD and the OpenUSD Exchange SDK ([docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/index.html), [github](https://github.com/NVIDIA-Omniverse/usd-exchange)) to demonstrate how to author consistent and correct USD:

- [`Asset Validator`](./source/assetValidator/README.md)
- [`createStage`](./source/createStage/README.md)
- [`createCameras`](./source/createCameras/README.md)
- [`createLights`](./source/createLights/README.md)
- [`createMaterials`](./source/createMaterials/README.md)
- [`createMesh`](./source/createMesh/README.md)
- [`createReferences`](./source/createReferences/README.md)
- [`createSkeleton`](./source/createSkeleton/README.md)
- [`createTransforms`](./source/createTransforms/README.md)
- [`setDisplayNames`](./source/setDisplayNames/README.md)

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

#### C++ Samples

Use the `run.sh` script (e.g. `./run.sh createStage`) to execute each program with a pre-configured environment.

> Tip: If you prefer to manage the environment yourself, add `<samplesRoot>/_build/linux64-x86_64/release` to your `LD_LIBRARY_PATH`.

For command line argument help, use `--help`
```bash
./run.sh createStage --help
```

#### Python Samples

Use the `python.sh` script (e.g. `./python.sh source/createStage/createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`
```bash
./python.sh source/createStage/createStage.py --help
```

### Windows
#### Building
Use the provided build script to download all dependencies (e.g USD), create the projects, and compile the code.
```bash
.\repo.bat build
```

#### C++ Samples

Use the `run.bat` script (e.g. `.\run.bat createStage`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\run.bat createStage --help
```

#### Python Samples

Use the `python.bat` script (e.g. `.\python.bat source\createStage\createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\python.bat source\createStage\createStage.py --help
```

#### Building within the Visual Studio IDE

To build within the VS IDE, open `_compiler\vs2019\USD-Exchange-Samples.sln` in Visual Studio 2019.  The sample C++ code can then be tweaked, debugged, rebuilt, etc. from there.

> Note : If the user installs the OpenUSD Exchange Samples into the `%LOCALAPPDATA%` folder, Visual Studio will not "Build" properly when changes are made because there is something wrong with picking up source changes.  Do one of these things to address the issue:
>  - `Rebuild` the project with every source change rather than `Build`
>  - Copy the OpenUSD Exchange Samples folder into another folder outside of `%LOCALAPPDATA%`
>  - Make a junction to a folder outside of %LOCALAPPDATA% and open the solution from there:
>    - `mklink /J C:\usd-exchange-samples %LOCALAPPDATA%\cloned-repos\usd-exchange-samples`

#### Changing the MSVC Compiler [Advanced]

When `repo.bat build` is run, a version of the Microsoft Visual Studio Compiler and the Windows 10 SDK are downloaded and referenced by the generated Visual Studio projects.  If a user wants the projects to use an installed version of Visual Studio 2019 then run `repo.bat build --use-devenv`.  Note, the build scripts are configured to tell `premake` to generate VS 2019 project files.  Some plumbing is required to support other Visual Studio versions.  Also, sometimes the projects are setup to use a particular Windows 10 SDK and MSVC build tools version, so it might be required to run the Visual Studio Installer to install the missing versions.

### Build and CI/CD Tools
The Samples repository uses the [Repo Tools Framework (`repo_man`)](https://docs.omniverse.nvidia.com/kit/docs/repo_man) to configure premake, packman, build and runtime dependencies, testing, formatting, and other tools. Packman is used as a dependency manager for packages like OpenUSD, the Omniverse Asset Validator, the OpenUSD Exchange SDK, and other items. The Samples use OpenUSD Exchange SDK's repo_man, premake, and packman tooling as templates for including and linking against OpenUSD, the OpenUSD Exchange SDK, and other dependencies.  These can serve as an example for the build and runtime configuration that a customer's application might require.  Here's a list of interesting files:

- [premake5.lua](./premake5.lua) - the build configuration file for the samples
- [prebuild.toml](./prebuild.toml) - consumed by the repo build tools to specify where runtime dependencies should be copied (beyond what `repo install_usdex` already installs)
- `_build/target-deps/usd-exchange/release/dev/tools/premake/usdex_build.lua` - the OpenUSD Exchange SDK's premake build configuration template file for including USD, the OpenUSD Exchange SDK itself, and other libraries.
  - this file isn't available until dependencies are fetched

For details on choosing and installing the OpenUSD Exchange SDK build flavors, features, or versions, see the [install_usdex](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/devtools.html#install-usdex) tool documentation.

## Using the OpenUSD Exchange SDK in an Application

See the [OpenUSD Exchange SDK Getting Started docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/docs/getting-started.html#integrate-into-an-application) for a walkthrough of how use the OpenUSD Exchange SDK and OpenUSD in your application.

## Sample Details

The samples listed are focused on these key concepts:
- OpenUSD
    - USD Cameras
    - USD Display Names
    - USD Lights
    - USD Materials
    - USD Meshes
    - USD Prim Names
    - USD Primvars
    - USD Stages
    - USD Xforms

### Running All Samples Together

The samples are intended to be run sequentially and will build up the USD stage that is originally created in the [`createStage`](./source/createStage/README.md) sample.  The can also be run independently and will either open or create a stage depending on whether it exists.  To run all of the samples sequentially with one command, type this in the command line after building:

```
Linux:
./repo.sh test -f testRunAll -e keep

Windows:
.\repo.bat test -f testRunAll -e keep
```

This will output the location of the C++ and Python generated stages after all of the samples have run sequentially.

## Issues with Self-Signed Certs
If the scripts from the Samples fail due to self-signed cert issues, a possible workaround would be to do this:

Install python-certifi-win32 which allows the windows certificate store to be used for TLS/SSL requests:

```bash
tools\packman\python.bat -m pip install python-certifi-win32 --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

## External Support

First search the existing [GitHub Issues](https://github.com/NVIDIA-Omniverse/usd-exchange-samples/issues) and the [USD Exchange Samples Forum](https://forums.developer.nvidia.com/c/omniverse/connectors/sample) to see if anyone has reported something similar.

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
