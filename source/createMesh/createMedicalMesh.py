# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import argparse
import sys
import random

# Internal imports
import common.sysUtils

common.sysUtils.initEnvPaths()

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, UsdGeom


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    xform = UsdGeom.Xform.Define(stage, "/Human")
    stage.SetDefaultPrim(xform.GetPrim())
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    if args.index is None:
        default_label_map = {1: 'Liver', 2: 'Spleen', 3: 'Pancreas', 4: 'Heart', 5: 'Body', 6: 'Gallbladder',
                7: 'Stomach', 8: 'Small_bowel', 9: 'Colon', 10: 'Kidney', 11: 'Veins', 12: 'Lungs',
                13: 'Spine', 14: 'Ribs', 15: 'Shoulders', 16: 'Hips', 17: 'Back_muscles'}
        label_map = default_label_map
    else:
        label_map = {args.index: args.value}
    color = [[random.random(), random.random(), random.random()] for _ in range(17)]
    for index, value in label_map.items():
        create_mesh = common.usdUtils.convert_to_mesh(
            args.input,
            label_value=index,
            smoothing_factor=0.5,
            reduction_ratio=0.0,
        )
        if create_mesh:
            meshPrim = common.usdUtils.createMeshFromVtk(stage.GetDefaultPrim(), value, create_mesh.GetOutput(), color[index-1], Gf.Vec3d(200, 30.0, 200.0))
        else:
            print(f"Failed to create mesh for {value}")

    if not meshPrim:
        print("Failure to create mesh prim")
        sys.exit(-1)

    usdex.core.saveStage(stage, "OpenUSD Exchange Samples")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a mesh using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", action="store", default="/mnt/hdd/Data/maisi_ct_generative/datasets/monai/nii/all_organs.nii.gz", help="Input image file")
    parser.add_argument("--index", action="store", required=False, default=None, type=int, help="Index of the label value")
    parser.add_argument("--value", action="store", required=False, default=None, help="Name of the label value")
    main(common.commandLine.parseCommonOptions(parser))
