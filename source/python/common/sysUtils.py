# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import os
import pathlib
import platform
import shutil
import sys
import tempfile


def getDefaultStagePath(extension):
    stageFile = "sample"
    tempDir = pathlib.Path(tempfile.gettempdir()) / "usdex"
    stagePath = tempDir / str(stageFile + extension)
    return stagePath.as_posix()


def copyTextureToStagePath(stagePath, textureFile: str):
    """
    Copies a texture file to the stage path's "textures" subdirectory

    The samples have light and material textures in the /resources/Materials directory.
    These are copied by this function to be near the stage on disk.

    Args:
        stagePath: The absolute path to the stage
        textureFile: The texture to copy

    Returns: The relative texture path for the asset attribute
    """
    texturesSubDir = "textures"
    scriptDir = pathlib.Path(__file__).resolve().parent
    textureSourcePath = scriptDir / pathlib.Path("../../../resources/Materials") / textureFile
    textureTargetPath = pathlib.Path(stagePath).parent / texturesSubDir / textureFile
    if not textureTargetPath.parent.exists():
        textureTargetPath.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(src=textureSourcePath, dst=textureTargetPath)

    return f"./{texturesSubDir}/{textureFile}"


def getAllSamples() -> list[str]:
    # Read samples from allSamples.txt
    # This file is in source/python/common, so we need to go up 4 levels to reach the root
    allSamplesPath = pathlib.Path(__file__).parent.parent.parent.parent / "allSamples.txt"
    samples = []
    try:
        with open(allSamplesPath, "r") as f:
            samples = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        self.fail(f"allSamples.txt not found at {allSamplesPath}")
    return samples
