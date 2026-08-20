# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import re
import shutil
import tempfile
import unittest
import zipfile

import usdex.core
import usdex.rtx
import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Sdr, Usd, UsdGeom, UsdShade, UsdUtils


def checkMdlSdrComplianceIssue(issue):
    """Bypass MDL shader compliance issues when the runtime does not provide an MDL parser."""
    if getattr(issue.rule, "__name__", None) != "ShaderSdrCompliance":
        return False
    if "mdl" in Sdr.Registry().GetAllShaderNodeSourceTypes():
        return False
    return bool(re.fullmatch(r"sourceType 'mdl' specified on shader prim .* not found in sdrRegistry\.", issue.message))


class CreateMaterialsTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createMaterials"
    defaultValidationIssuePredicates = [checkMdlSdrComplianceIssue]

    PREVIEW_SURFACE = 0
    OPENPBR = 1
    OMNIPBR = 2
    PREVIEW_SURFACE_GLASS = 3
    OPENPBR_GLASS = 4
    OMNIPBR_GLASS = 5
    OMNIPBR_UVW = 6
    PREVIEW_SURFACE_EMISSIVE = 7
    OPENPBR_EMISSIVE = 8
    OMNIPBR_EMISSIVE = 9
    PREVIEW_SURFACE_EMISSIVE_TEXTURE = 10
    OPENPBR_EMISSIVE_TEXTURE = 11
    OMNIPBR_EMISSIVE_TEXTURE = 12
    MESH_WITH_GEOMSUBSETS = 13

    # Test the createMaterials program
    # Testing:
    # - it creates meshes and spheres under the materialSampleGrid Xform
    # - the geometry and materials should have the correct names (depending on existing sibling prims)
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage

    def _getMaterial(self, stage, materialScopePath, materialName):
        prim = stage.GetPrimAtPath(materialScopePath.AppendPath(materialName))
        self.assertTrue(prim)
        material = UsdShade.Material(prim)
        self.assertTrue(material)
        self.assertIsInstance(material, UsdShade.Material)
        return material

    def _assertMesh(self, stage, geometryPrim, primName):
        prim = stage.GetPrimAtPath(geometryPrim.GetPath().AppendChild(primName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Mesh(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Mesh)
        return prim

    def _assertSphere(self, stage, geometryPrim, primName):
        prim = stage.GetPrimAtPath(geometryPrim.GetPath().AppendChild(primName))
        self.assertTrue(prim)
        typedPrim = UsdGeom.Sphere(prim)
        self.assertTrue(typedPrim)
        self.assertIsInstance(typedPrim, UsdGeom.Sphere)

        # refinementEnableOverride and refinementLevel are custom attributes for the sphere prim
        attr = prim.GetAttribute("refinementEnableOverride")
        self.assertTrue(attr)
        self.assertEqual(attr.Get(), True)
        self.assertTrue(attr.IsCustom())

        attr = prim.GetAttribute("refinementLevel")
        self.assertTrue(attr)
        self.assertEqual(attr.Get(), 2)
        self.assertTrue(attr.IsCustom())
        return prim

    def _assertMaterialBound(self, prim, material):
        self.assertTrue(UsdShade.MaterialBindingAPI(prim))
        boundMaterial = UsdShade.MaterialBindingAPI.ComputeBoundMaterials([prim])[0][0]
        self.assertTrue(boundMaterial)
        self.assertEqual(boundMaterial.GetPrim().GetPath(), material.GetPrim().GetPath())

    def _assertTextureInputsExist(self, stage, material, textureInputs):
        for textureInput in textureInputs:
            texPath = material.GetInput(textureInput).Get().path
            absPath = stage.GetRootLayer().ComputeAbsolutePath(texPath)
            self.assertTrue(pathlib.Path(absPath).exists())

    def _assertEmissiveColor(self, material):
        emissiveColor = material.GetInput("emissiveColor")
        self.assertTrue(emissiveColor)
        self.assertTrue(Gf.IsClose(emissiveColor.Get(), Gf.Vec3f(1.0, 0.77, 0.56), 1e-6))

    def _assertEmissiveTexture(self, material):
        emissiveTexture = material.GetInput("EmissiveTexture")
        self.assertTrue(emissiveTexture)
        self.assertEqual(emissiveTexture.Get().path, "./textures/Fieldstone/Fieldstone_N.png")

    def _assertMaterialInterfaceInputs(self, material, inputNames):
        materialInputNames = {materialInput.GetBaseName() for materialInput in material.GetInterfaceInputs()}
        for inputName in inputNames:
            self.assertIn(inputName, materialInputNames)

    def _assertOmniPbrExamplesAbsent(self, stage, geometryPrim, materialScopePath, geomNames, materialNames):
        for example in [
            self.OMNIPBR,
            self.OMNIPBR_GLASS,
            self.OMNIPBR_UVW,
            self.OMNIPBR_EMISSIVE,
            self.OMNIPBR_EMISSIVE_TEXTURE,
        ]:
            self.assertFalse(stage.GetPrimAtPath(geometryPrim.GetPath().AppendChild(geomNames[example])))
            self.assertFalse(stage.GetPrimAtPath(materialScopePath.AppendPath(materialNames[example])))

    def _checkStageContents(self, stagePath, geomNames, materialNames, tabletMaterialNames, includeOmniPbr=True):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        defaultPrim = stage.GetDefaultPrim()
        self.assertTrue(defaultPrim)

        materialScopePath = defaultPrim.GetPath().AppendPath(UsdUtils.GetMaterialsScopeName())
        geometryPrim = stage.GetPrimAtPath(defaultPrim.GetPath().AppendChild("materialSampleGrid"))
        self.assertTrue(geometryPrim)
        geometryXform = UsdGeom.Xform(geometryPrim)
        self.assertTrue(geometryXform)
        self.assertIsInstance(geometryXform, UsdGeom.Xform)
        self.assertTrue(Gf.IsClose(usdex.core.getLocalTransform(geometryPrim).GetTranslation(), Gf.Vec3d(-3.75, 4.5, 0.0), 1e-6))

        # Check the Preview Surface material and mesh.
        previewMat = self._getMaterial(stage, materialScopePath, materialNames[self.PREVIEW_SURFACE])
        self._assertMaterialBound(self._assertMesh(stage, geometryPrim, geomNames[self.PREVIEW_SURFACE]), previewMat)
        self.assertEqual(
            usdex.core.computeEffectivePreviewSurfaceShader(previewMat).GetPrim().GetPath(),
            usdex.rtx.computeEffectiveMdlSurfaceShader(previewMat).GetPrim().GetPath(),
        )

        # Check the textured OpenPBR material and mesh.
        textureInputs = ["ColorTexture", "NormalTexture", "ORMTexture"]
        openPbrMat = self._getMaterial(stage, materialScopePath, materialNames[self.OPENPBR])
        self._assertTextureInputsExist(stage, openPbrMat, textureInputs)
        self.assertTrue(usdex.core.computeEffectiveMtlxSurfaceShader(openPbrMat))
        self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(openPbrMat))
        self._assertMaterialBound(self._assertMesh(stage, geometryPrim, geomNames[self.OPENPBR]), openPbrMat)

        if includeOmniPbr:
            # Check the textured OmniPBR material and mesh.
            omniPbrMat = self._getMaterial(stage, materialScopePath, materialNames[self.OMNIPBR])
            self._assertTextureInputsExist(stage, omniPbrMat, textureInputs)
            self.assertTrue(usdex.rtx.computeEffectiveMdlSurfaceShader(omniPbrMat))
            self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(omniPbrMat))
            self._assertMaterialBound(self._assertMesh(stage, geometryPrim, geomNames[self.OMNIPBR]), omniPbrMat)

        # Check the glass materials and spheres.
        previewGlassMat = self._getMaterial(stage, materialScopePath, materialNames[self.PREVIEW_SURFACE_GLASS])
        self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(previewGlassMat))
        self._assertMaterialInterfaceInputs(previewGlassMat, ["diffuseColor", "ior", "opacity", "roughness"])
        self._assertMaterialBound(self._assertSphere(stage, geometryPrim, geomNames[self.PREVIEW_SURFACE_GLASS]), previewGlassMat)

        openPbrGlassMat = self._getMaterial(stage, materialScopePath, materialNames[self.OPENPBR_GLASS])
        self.assertTrue(usdex.core.computeEffectiveMtlxSurfaceShader(openPbrGlassMat))
        self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(openPbrGlassMat))
        self._assertMaterialBound(self._assertSphere(stage, geometryPrim, geomNames[self.OPENPBR_GLASS]), openPbrGlassMat)

        if includeOmniPbr:
            omniPbrGlassMat = self._getMaterial(stage, materialScopePath, materialNames[self.OMNIPBR_GLASS])
            self.assertTrue(usdex.rtx.computeEffectiveMdlSurfaceShader(omniPbrGlassMat))
            self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(omniPbrGlassMat))
            self._assertMaterialBound(self._assertSphere(stage, geometryPrim, geomNames[self.OMNIPBR_GLASS]), omniPbrGlassMat)

            # Check the OmniPBR UVW projection material and sphere.
            uvwMat = self._getMaterial(stage, materialScopePath, materialNames[self.OMNIPBR_UVW])
            mdlShader = usdex.rtx.computeEffectiveMdlSurfaceShader(uvwMat)
            self.assertTrue(mdlShader.GetInput("project_uvw").Get())
            self.assertTrue(mdlShader.GetInput("world_or_object").Get())
            self.assertAlmostEqual(mdlShader.GetInput("texture_scale").Get(), Gf.Vec2f(1.0))
            self._assertMaterialBound(self._assertSphere(stage, geometryPrim, geomNames[self.OMNIPBR_UVW]), uvwMat)

        # Check the emissive color materials and spheres.
        emissiveExamples = [self.PREVIEW_SURFACE_EMISSIVE, self.OPENPBR_EMISSIVE]
        if includeOmniPbr:
            emissiveExamples.append(self.OMNIPBR_EMISSIVE)
        for example in emissiveExamples:
            emissiveMat = self._getMaterial(stage, materialScopePath, materialNames[example])
            self._assertEmissiveColor(emissiveMat)
            self._assertMaterialBound(self._assertSphere(stage, geometryPrim, geomNames[example]), emissiveMat)

        # Check the emissive texture materials and meshes.
        emissiveTextureExamples = [self.PREVIEW_SURFACE_EMISSIVE_TEXTURE, self.OPENPBR_EMISSIVE_TEXTURE]
        if includeOmniPbr:
            emissiveTextureExamples.append(self.OMNIPBR_EMISSIVE_TEXTURE)
        for example in emissiveTextureExamples:
            emissiveTextureMat = self._getMaterial(stage, materialScopePath, materialNames[example])
            self._assertEmissiveTexture(emissiveTextureMat)
            self._assertMaterialBound(self._assertMesh(stage, geometryPrim, geomNames[example]), emissiveTextureMat)

        if not includeOmniPbr:
            self._assertOmniPbrExamplesAbsent(stage, geometryPrim, materialScopePath, geomNames, materialNames)

        # Check the mesh with GeomSubsets and its bound materials.
        meshPrim = self._assertMesh(stage, geometryPrim, geomNames[self.MESH_WITH_GEOMSUBSETS])
        self.assertTrue(Gf.IsClose(usdex.core.getLocalTransform(meshPrim).GetTranslation(), Gf.Vec3d(2.25, -1.5, 0.1), 1e-6))
        mesh = UsdGeom.Mesh(meshPrim)
        self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), 10)
        self.assertEqual(UsdGeom.Subset.GetFamilyType(mesh, UsdShade.Tokens.materialBind), UsdGeom.Tokens.partition)

        expectedSubsets = [
            ("front", [6, 7, 8, 9], tabletMaterialNames[0], Gf.Vec3f(0.0, 0.0, 0.0), 0.0, 0.0),
            ("body", [0, 1, 2, 3, 4], tabletMaterialNames[1], Gf.Vec3f(0.6, 0.8, 0.5), 0.6, 1.0),
            ("screen", [5], tabletMaterialNames[2], Gf.Vec3f(1.0, 1.0, 1.0), 0.0, 0.0),
        ]
        for subsetName, indices, materialName, color, roughness, metallic in expectedSubsets:
            subsetPrim = meshPrim.GetChild(subsetName)
            self.assertTrue(subsetPrim)
            subset = UsdGeom.Subset(subsetPrim)
            self.assertTrue(subset)
            self.assertEqual(subset.GetElementTypeAttr().Get(), UsdGeom.Tokens.face)
            self.assertEqual(subset.GetFamilyNameAttr().Get(), UsdShade.Tokens.materialBind)
            self.assertEqual(list(subset.GetIndicesAttr().Get()), indices)

            material = self._getMaterial(stage, materialScopePath, materialName)
            self.assertTrue(usdex.core.computeEffectivePreviewSurfaceShader(material))
            # Values live on the material interface after addPreviewMaterialInterface().
            self.assertTrue(Gf.IsClose(material.GetInput("diffuseColor").Get(), color, 1e-6))
            self.assertAlmostEqual(material.GetInput("roughness").Get(), roughness)
            self.assertAlmostEqual(material.GetInput("metallic").Get(), metallic)
            self._assertMaterialInterfaceInputs(material, ["diffuseColor", "metallic", "opacity", "roughness"])
            self._assertMaterialBound(subsetPrim, material)

        # Screen material is emissive white.
        screenMat = self._getMaterial(stage, materialScopePath, tabletMaterialNames[2])
        emissiveColor = screenMat.GetInput("emissiveColor")
        self.assertTrue(emissiveColor)
        self.assertTrue(Gf.IsClose(emissiveColor.Get(), Gf.Vec3f(1.0, 1.0, 1.0), 1e-6))
        self._assertMaterialInterfaceInputs(screenMat, ["emissiveColor"])

    def runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            geomNames = [
                "previewSurfaceMesh",
                "openPbrMesh",
                "omniPbrMesh",
                "previewSurfaceGlassSphere",
                "openPbrGlassSphere",
                "omniPbrGlassSphere",
                "omniPbrUvwSphere",
                "previewSurfaceEmissiveSphere",
                "openPbrEmissiveSphere",
                "omniPbrEmissiveSphere",
                "previewSurfaceEmissiveTexture",
                "openPbrEmissiveTexture",
                "omniPbrEmissiveTexture",
                "meshWithGeomsubsets",
            ]
            materialNames = [
                "previewSurface",
                "openPbr",
                "omniPbr",
                "previewSurfaceGlass",
                "openPbrGlass",
                "omniPbrGlass",
                "omniPbrUvw",
                "previewSurfaceEmissive",
                "openPbrEmissive",
                "omniPbrEmissive",
                "previewSurfaceEmissiveTexture",
                "openPbrEmissiveTexture",
                "omniPbrEmissiveTexture",
            ]
            tabletMaterialNames = [
                "tabletFront",
                "tabletBody",
                "tabletScreen",
            ]

            def addSuffix(names, index):
                suffix = "" if index == 0 else f"_{index}"
                return [f"{name}{suffix}" for name in names]

            for args in argsRuns:
                for i in range(2):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(
                        args[0],
                        addSuffix(geomNames, i),
                        addSuffix(materialNames, i),
                        addSuffix(tabletMaterialNames, i),
                    )
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test USDZ output includes textures but skips OmniPBR examples and MDL modules
            stagePath = pathlib.Path(tempDir / "test_stage_usdz.usdc")
            usdzPath = stagePath.with_suffix(".usdz")
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", stagePath.as_posix(), "--usdz")
            self.assertEqual(return_code, 0, output)
            self.assertNotIn("Failed to resolve reference", output)
            utils.fileFormat.checkUsdzPackage(
                self,
                usdzPath.as_posix(),
                [
                    "test_stage_usdz.usdc",
                    "textures/Fieldstone/Fieldstone_N.png",
                    "textures/Fieldstone/Fieldstone_BaseColor.png",
                    "textures/Fieldstone/Fieldstone_ORM.png",
                ],
            )
            with zipfile.ZipFile(usdzPath) as archive:
                self.assertFalse(any(name.endswith(".mdl") for name in archive.namelist()))
            self._checkStageContents(stagePath.as_posix(), geomNames, materialNames, tabletMaterialNames, includeOmniPbr=False)

            # Test relative path calculation in the program.  These pollute the repo, but they clean up after themselves
            localStage = "local_test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, geomNames, materialNames, tabletMaterialNames)
            pathlib.Path.unlink(pathlib.Path(localStage))
            shutil.rmtree("textures")

            localStage = "local_directory/test_stage.usdc"
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", localStage)
            self.assertEqual(return_code, 0, output)
            self._checkStageContents(localStage, geomNames, materialNames, tabletMaterialNames)
            shutil.rmtree("local_directory")

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
