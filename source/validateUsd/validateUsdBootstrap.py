# SPDX-FileCopyrightText: Copyright (c) 2022-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import re

import usd_validation_nvidia
from pxr import Ar, Sdr
from usd_validation_nvidia import ValidationArgsExec, create_validation_parser

_MDL_SDR_COMPLIANCE_MESSAGE = re.compile(r"sourceType 'mdl' specified on shader prim .* not found in sdrRegistry\.")


def _isMdlSdrComplianceIssue(issue):
    if "mdl" in Sdr.Registry().GetAllShaderNodeSourceTypes():
        return False
    return bool(_MDL_SDR_COMPLIANCE_MESSAGE.fullmatch(issue.message))


mdlSdrComplianceIssuePredicate = usd_validation_nvidia.IssuePredicates.And(
    usd_validation_nvidia.IssuePredicates.IsRule(usd_validation_nvidia.UsdShadeShaderSdrCompliance),
    _isMdlSdrComplianceIssue,
)


class SamplesValidationArgsExec(ValidationArgsExec):

    @property
    def predicate(self):
        return usd_validation_nvidia.IssuePredicates.And(
            super().predicate,
            usd_validation_nvidia.IssuePredicates.Not(mdlSdrComplianceIssuePredicate),
        )


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
        args = SamplesValidationArgsExec(parser.parse_args())
        args.run_validation()


if __name__ == "__main__":
    main()
