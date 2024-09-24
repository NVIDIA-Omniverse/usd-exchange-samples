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

To build the OpenUSD Exchange SDK yourself, use `repo.bat build` or `repo.sh build`, depending on your local platform.

The `repo build` command accepts additional arguments (e.g. `-config release`), see `repo build --help` for more information. Internally, `repo build` is using [Premake](https://premake.github.io) to perform cross-platform builds. See the `premake5.lua` file a the root of the repository to learn how the libraries are compiled.

## Testing

To run all of the tests, use `repo.bat test` or `repo.sh test`, depending on your local platform.

If you want to isolate the tests, `repo test -f <pattern>` will filter down to a single test file or test pattern. See `repo test -h` for more information.
