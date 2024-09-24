# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# USD imports
from pxr import Sdf, Usd, UsdGeom, UsdLux


def checkLayerFormat(testClass, stagePath, textFlag):
    # Check the stage/layer file format/encoding
    if ".usda" in stagePath or textFlag:
        testClass.assertTrue(Sdf.FileFormat.FindById("usda").CanRead(stagePath))
    else:
        testClass.assertTrue(Sdf.FileFormat.FindById("usdc").CanRead(stagePath))
