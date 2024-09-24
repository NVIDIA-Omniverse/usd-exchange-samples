# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import os

# Internal imports
import common.sysUtils

# Setup PATH and PYTHONPATH
common.sysUtils.initEnvPaths()

from omni.asset_validator import ValidationArgsExec, create_validation_parser
from pxr import Ar


def main():
    # Define the search path that allows "OmniPBR.mdl" and "OmniGlass.mdl" to resolve
    searchPaths = [common.sysUtils.getCoreMaterialsPath()]

    # Create a default resolver context with the search paths
    resolverContext = Ar.DefaultResolverContext(searchPaths)

    # Bind the resolver context to make it the current context
    with Ar.ResolverContextBinder(resolverContext):
        parser = create_validation_parser()
        args = ValidationArgsExec(parser.parse_args())
        args.run_validation()


if __name__ == "__main__":
    main()
