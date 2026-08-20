# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import zipfile

# USD imports
from pxr import Ar, Sdf, Usd, UsdUtils


def checkLayerFormat(testClass, stagePath, textFlag):
    # Check the stage/layer file format/encoding
    if ".usda" in stagePath or textFlag:
        testClass.assertTrue(Sdf.FileFormat.FindById("usda").CanRead(stagePath))
    else:
        testClass.assertTrue(Sdf.FileFormat.FindById("usdc").CanRead(stagePath))


def _checkPackagedPath(testClass, usdzPathObj, archiveNames, resolvedPath, sourceDescription):
    testClass.assertTrue(resolvedPath, f"{sourceDescription} did not resolve to a path")
    testClass.assertTrue(
        Ar.IsPackageRelativePath(resolvedPath),
        f"{sourceDescription} resolved outside USDZ package {usdzPathObj}: {resolvedPath}",
    )

    # A localized asset should resolve to this exact package, using the package-relative
    # form "/path/to/package.usdz[path/inside/package.ext]".
    packagePath, packagedPath = Ar.SplitPackageRelativePathOuter(resolvedPath)
    testClass.assertEqual(
        pathlib.Path(packagePath).resolve(),
        usdzPathObj.resolve(),
        f"{sourceDescription} resolved into unexpected package {packagePath}; expected {usdzPathObj}",
    )

    # The path inside the package should be a normal relative archive path, and
    # it should name an item that was actually written into the zip archive.
    packagedPathObj = pathlib.PurePosixPath(packagedPath)
    testClass.assertFalse(
        packagedPathObj.is_absolute() or ".." in packagedPathObj.parts,
        f"{sourceDescription} resolved to invalid package-relative path {packagedPath}",
    )

    # USD localization may move dependencies from absolute or otherwise awkward
    # source paths into generated directories such as "0/" or "1/". That is a
    # valid USDZ package, but these samples should author package-friendly paths
    # that preserve their intended relative layout.
    testClass.assertFalse(
        packagedPathObj.parts and packagedPathObj.parts[0].isdigit(),
        f"{sourceDescription} resolved to generated package directory {packagedPath}; samples should author relative asset paths",
    )
    testClass.assertIn(packagedPathObj.as_posix(), archiveNames, f"{sourceDescription} resolved to missing package item {packagedPath}")


def _checkUsdzAssetPathsLocalized(testClass, usdzPathObj, archiveNames):
    # ComputeAllDependencies catches composition arcs such as references, payloads,
    # sublayers, and asset-valued dependencies discovered by USD. This matches
    # the dependency source used by USD's compliance checker.
    layerDeps, assetDeps, unresolvedDeps = UsdUtils.ComputeAllDependencies(Sdf.AssetPath(usdzPathObj.as_posix()))
    testClass.assertFalse(unresolvedDeps, f"USDZ package {usdzPathObj} has unresolved asset paths: {unresolvedDeps}")

    for layer in layerDeps:
        layerPath = layer.realPath or layer.identifier
        if pathlib.Path(layerPath).resolve() == usdzPathObj.resolve():
            continue
        _checkPackagedPath(testClass, usdzPathObj, archiveNames, layerPath, f"Layer dependency {layer.identifier}")

    for assetPath in assetDeps:
        _checkPackagedPath(testClass, usdzPathObj, archiveNames, assetPath, f"Asset dependency {assetPath}")


def checkUsdzPackage(testClass, usdzPath, expectedArchiveNames=None):
    usdzPathObj = pathlib.Path(usdzPath)
    testClass.assertTrue(usdzPathObj.exists(), f"USDZ package {usdzPathObj} does not exist")
    testClass.assertTrue(zipfile.is_zipfile(usdzPathObj), f"USDZ package {usdzPathObj} is not a zip archive")

    with zipfile.ZipFile(usdzPathObj) as archive:
        archiveNames = archive.namelist()

    testClass.assertGreater(len(archiveNames), 0, f"USDZ package {usdzPathObj} is empty")
    if expectedArchiveNames:
        for expectedName in expectedArchiveNames:
            testClass.assertIn(expectedName, archiveNames)

    stage = Usd.Stage.Open(usdzPathObj.as_posix())
    testClass.assertTrue(stage, f"Unable to open USDZ package {usdzPathObj}")
    testClass.assertTrue(stage.GetDefaultPrim(), f"USDZ package {usdzPathObj} has no default prim")
    _checkUsdzAssetPathsLocalized(testClass, usdzPathObj, archiveNames)
    testClass.runAssetValidator(usdzPathObj.as_posix())
