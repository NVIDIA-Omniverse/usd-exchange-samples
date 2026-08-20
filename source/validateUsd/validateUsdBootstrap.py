# SPDX-FileCopyrightText: Copyright (c) 2022-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os

from pxr import Ar
from usd_validation_nvidia import ValidationArgsExec, create_validation_parser


def getCoreMaterialsPath():
    scriptToCoreMaterialsPath = "../../_build/target-deps/omni_core_materials/Base"
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    absCoreMatPath = os.path.abspath(os.path.join(scriptdir, scriptToCoreMaterialsPath))
    return absCoreMatPath


def main():
    # Define the search path that allows "OmniPBR.mdl" and "OmniGlass.mdl" to resolve
    searchPaths = [getCoreMaterialsPath()]

    # Create a default resolver context with the search paths
    resolverContext = Ar.DefaultResolverContext(searchPaths)

    # Bind the resolver context to make it the current context
    with Ar.ResolverContextBinder(resolverContext):
        parser = create_validation_parser()
        args = ValidationArgsExec(parser.parse_args())
        args.run_validation()


if __name__ == "__main__":
    main()
