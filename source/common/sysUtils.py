# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import os
import pathlib
import platform
import shutil
import sys
import tempfile


def initEnvPaths():
    # Set PATH, and PYTHONPATH
    scriptToRuntimePath = f"../../_build/{platform.system().lower()}-x86_64/release"
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    appPath = os.path.abspath(os.path.join(scriptdir, scriptToRuntimePath))
    os.environ["PATH"] += os.pathsep + appPath
    sys.path.append(os.path.join(appPath, "python"))
    sys.path.append(os.path.join(appPath, "scripts"))

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(appPath)


def getDefaultStagePath(extension):
    stageFile = "sample"
    tempDir = pathlib.Path(tempfile.gettempdir()) / "usdex"
    stagePath = tempDir / str(stageFile + extension)
    return stagePath.as_posix()


def getCoreMaterialsPath():
    scriptToCoreMaterialsPath = f"../../_build/target-deps/omni_core_materials/Base"
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    absCoreMatPath = os.path.abspath(os.path.join(scriptdir, scriptToCoreMaterialsPath))
    return absCoreMatPath


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
    textureSourcePath = scriptDir / pathlib.Path("../../resources/Materials") / textureFile
    textureTargetPath = pathlib.Path(stagePath).parent / texturesSubDir / textureFile
    if not textureTargetPath.parent.exists():
        textureTargetPath.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(src=textureSourcePath, dst=textureTargetPath)

    return f"./{texturesSubDir}/{textureFile}"
