# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import pathlib
import sys

# Internal imports
import common.sysUtils


def parseCommonOptions(parser):
    stagePath = common.sysUtils.getDefaultStagePath(".usdc")

    parser.add_argument("-a", "--usda", action="store_true", help="Output a text stage rather than binary")
    parser.add_argument("-p", "--path", action="store", default=stagePath, help="Alternate destination stage path")
    args = parser.parse_args()
    args.fileFormatArgs = dict()

    """
    Stage path and format:
     --path c:\folder\stage.usdc --usda -> error about invalid arg combo
     --path c:\folder\stage.usda --usda -> redundant but silent pass
     --path c:\folder\stage.usd --usda -> use file format args to steer the layer format
    """

    if args.usda and stagePath == args.path:
        args.path = common.sysUtils.getDefaultStagePath(".usda")
    else:
        pathExtension = str(pathlib.Path(args.path).suffix).casefold()
        if args.usda and ".usdc" == pathExtension:
            print(f"Error parsing arguments: Inconsistent use of --usda with a .usdc stage")
            parser.print_help()
            sys.exit(2)
        elif args.usda and ".usd" == pathExtension:
            # Usd.UsdFileFormat.Tokens.FormatArg doesn't exist, but it should
            # Usd.UsdaFileFormat.Tokens.Id doesn't exist, but it should
            args.fileFormatArgs = {"format": "usda"}

    return args
