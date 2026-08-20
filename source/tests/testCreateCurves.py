# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import pathlib
import tempfile
import unittest

import usdex.core
import utils.BaseTestCase as BaseTestCaseModule
import utils.fileFormat
import utils.shell
from pxr import Gf, Usd, UsdGeom, Vt


class CreateCurvesTestCase(BaseTestCaseModule.BaseTestCase):

    sampleName = "createCurves"

    # Test the createCurves program
    # Testing:
    # - it creates fourteen UsdGeom.BasisCurves prims in seven feature pairs under a curvesXform parent
    # - each pair compares linear and cubic curve types for batched multi-curve, widths, displayColor,
    #   displayOpacity, ribbon normals, and periodic wrap
    # - curvesXform and curve local transforms match the hardcoded gallery layout
    # - it uses the "usda" argument
    # - it runs properly with or without an existing stage

    # Expected child prim names under curvesXform (see createCurves sample)
    CURVE_NAMES = [
        "linearBatched",
        "cubicBatched",
        "linearUniformWidth",
        "cubicUniformWidth",
        "linearVertexWidth",
        "cubicVertexWidth",
        "linearDisplayColor",
        "cubicDisplayColor",
        "linearVertexDisplayColor",
        "cubicVertexDisplayColor",
        "linearRibbon",
        "cubicRibbon",
        "linearPeriodicWrap",
        "cubicPeriodicWrap",
    ]

    # Expected control points for open single-curve prims (linearUniformWidth through cubicRibbon)
    LINEAR_OPEN_POINTS = [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.267, 0.0, 0.3),
        Gf.Vec3f(0.53, 0.0, 0.2),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.356, 0.0, 0.15),
        Gf.Vec3f(1.844, 0.0, 0.5),
        Gf.Vec3f(2.4, 0.0, 0.45),
    ]

    CUBIC_OPEN_POINTS = [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.3, 0.0, 0.6),
        Gf.Vec3f(0.45, 0.0, 0.15),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.35, 0.0, -0.15),
        Gf.Vec3f(1.8, 0.0, 0.9),
        Gf.Vec3f(2.4, 0.0, 0.45),
    ]

    # Expected control points for batched multi-curve prims (linearBatched, cubicBatched)
    BATCHED_LINEAR_POINTS = [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.267, 0.0, 0.3),
        Gf.Vec3f(0.53, 0.0, 0.2),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.356, 0.0, 0.15),
        Gf.Vec3f(1.844, 0.0, 0.5),
        Gf.Vec3f(2.4, 0.0, 0.45),
        Gf.Vec3f(0.0, 0.0, -0.3),
        Gf.Vec3f(0.267, 0.0, 0.0),
        Gf.Vec3f(0.53, 0.0, -0.1),
        Gf.Vec3f(0.9, 0.0, -0.3),
        Gf.Vec3f(1.356, 0.0, -0.15),
    ]

    BATCHED_CUBIC_POINTS = [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.3, 0.0, 0.6),
        Gf.Vec3f(0.45, 0.0, 0.15),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.35, 0.0, -0.15),
        Gf.Vec3f(1.8, 0.0, 0.9),
        Gf.Vec3f(2.4, 0.0, 0.45),
        Gf.Vec3f(0.0, 0.0, -0.3),
        Gf.Vec3f(0.3, 0.0, 0.3),
        Gf.Vec3f(0.45, 0.0, -0.15),
        Gf.Vec3f(0.9, 0.0, -0.3),
    ]

    # Expected per-vertex displayColor values for linearVertexDisplayColor and cubicVertexDisplayColor
    VERTEX_DISPLAY_COLORS = [
        Gf.Vec3f(1.0, 0.0, 0.0),
        Gf.Vec3f(1.0, 0.5, 0.0),
        Gf.Vec3f(1.0, 1.0, 0.0),
        Gf.Vec3f(0.0, 1.0, 0.0),
        Gf.Vec3f(0.0, 1.0, 1.0),
        Gf.Vec3f(0.0, 0.0, 1.0),
        Gf.Vec3f(0.5, 0.0, 1.0),
    ]

    # Expected per-vertex displayOpacity values (1.0 to 0.0 gradient) for linearVertexDisplayColor and cubicVertexDisplayColor
    VERTEX_DISPLAY_OPACITIES = [1.0, 0.83, 0.67, 0.50, 0.33, 0.17, 0.0]

    # Expected indexed normal for linearRibbon and cubicRibbon
    RIBBON_NORMAL = Gf.Vec3f(0.0, -1.0, 0.0)

    def _checkBasisCurvesPrim(self, prim, curve_type, wrap):
        """Check that a prim is a valid UsdGeom.BasisCurves with the expected type and wrap."""
        self.assertTrue(prim)
        typed_prim = UsdGeom.BasisCurves(prim)
        self.assertTrue(typed_prim)
        self.assertIsInstance(typed_prim, UsdGeom.BasisCurves)
        self.assertEqual(typed_prim.GetTypeAttr().Get(), curve_type)
        self.assertEqual(typed_prim.GetWrapAttr().Get(), wrap)
        if curve_type == UsdGeom.Tokens.cubic:
            self.assertEqual(typed_prim.GetBasisAttr().Get(), UsdGeom.Tokens.bezier)

    def _checkStageContents(self, stagePath, curvesXformName, curve_prim_names):
        self.runAssetValidator(stagePath)

        stage = Usd.Stage.Open(stagePath)
        self.assertTrue(stage)

        default_prim = stage.GetDefaultPrim()
        self.assertTrue(default_prim)

        # Check the curvesXform parent and its world-space center
        curves_xform_prim = stage.GetPrimAtPath(default_prim.GetPath().AppendChild(curvesXformName))
        self.assertTrue(curves_xform_prim)
        typed_prim = UsdGeom.Xform(curves_xform_prim)
        self.assertTrue(typed_prim)
        self.assertIsInstance(typed_prim, UsdGeom.Xform)
        xform_translation, _, _, _, _ = usdex.core.getLocalTransformComponents(curves_xform_prim)
        self.assertTrue(Gf.IsClose(xform_translation, Gf.Vec3d(-6.3, 9.0, 2.0), 1e-6))

        name_to_path = {name: curves_xform_prim.GetPath().AppendChild(name) for name in curve_prim_names}

        # Check batched multi-curve (linearBatched, cubicBatched)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[0]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[1]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        linear_batched = UsdGeom.BasisCurves(stage.GetPrimAtPath(name_to_path[curve_prim_names[0]]))
        cubic_batched = UsdGeom.BasisCurves(stage.GetPrimAtPath(name_to_path[curve_prim_names[1]]))
        self.assertEqual(linear_batched.GetCurveVertexCountsAttr().Get(), Vt.IntArray([7, 5]))
        self.assertEqual(cubic_batched.GetCurveVertexCountsAttr().Get(), Vt.IntArray([7, 4]))
        self.assertEqual(list(linear_batched.GetPointsAttr().Get()), self.BATCHED_LINEAR_POINTS)
        self.assertEqual(list(cubic_batched.GetPointsAttr().Get()), self.BATCHED_CUBIC_POINTS)
        for index in (0, 1):
            widths_primvar = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.12)

        # Check constant width (linearUniformWidth, cubicUniformWidth)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[2]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[3]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        linear_uniform = UsdGeom.BasisCurves(stage.GetPrimAtPath(name_to_path[curve_prim_names[2]]))
        cubic_uniform = UsdGeom.BasisCurves(stage.GetPrimAtPath(name_to_path[curve_prim_names[3]]))
        self.assertEqual(list(linear_uniform.GetPointsAttr().Get()), self.LINEAR_OPEN_POINTS)
        self.assertEqual(list(cubic_uniform.GetPointsAttr().Get()), self.CUBIC_OPEN_POINTS)
        for index in (2, 3):
            widths_primvar = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.12)

        # Check per-vertex width (linearVertexWidth, cubicVertexWidth)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[4]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[5]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        for index in (4, 5):
            widths_primvar = UsdGeom.PrimvarsAPI(stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.vertex)
            self.assertEqual(len(widths_primvar.Get()), 7)

        # Check constant displayColor (linearDisplayColor, cubicDisplayColor)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[6]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[7]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        for index in (6, 7):
            prim = stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])
            display_color = UsdGeom.BasisCurves(prim).GetDisplayColorPrimvar()
            self.assertTrue(display_color.HasAuthoredValue())
            self.assertEqual(display_color.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertEqual(display_color.Get()[0], Gf.Vec3f(1.0, 0.5, 0.2))
            widths_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.12)

        # Check per-vertex displayColor and displayOpacity (linearVertexDisplayColor, cubicVertexDisplayColor)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[8]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[9]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        for index in (8, 9):
            prim = stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])
            display_color = UsdGeom.BasisCurves(prim).GetDisplayColorPrimvar()
            self.assertTrue(display_color.HasAuthoredValue())
            self.assertEqual(display_color.GetInterpolation(), UsdGeom.Tokens.vertex)
            self.assertEqual(list(display_color.Get()), self.VERTEX_DISPLAY_COLORS)
            display_opacity = UsdGeom.BasisCurves(prim).GetDisplayOpacityPrimvar()
            self.assertTrue(display_opacity.HasAuthoredValue())
            self.assertEqual(display_opacity.GetInterpolation(), UsdGeom.Tokens.vertex)
            self.assertEqual(len(display_opacity.Get()), len(self.VERTEX_DISPLAY_OPACITIES))
            # Compare at two decimal places to account for float32 storage
            for actual, expected in zip(display_opacity.Get(), self.VERTEX_DISPLAY_OPACITIES):
                self.assertAlmostEqual(actual, expected, places=2)
            widths_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.12)

        # Check oriented ribbon (linearRibbon, cubicRibbon)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[10]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.nonperiodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[11]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.nonperiodic,
        )
        for index in (10, 11):
            prim = stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])
            typed_prim = UsdGeom.BasisCurves(prim)
            self.assertEqual(typed_prim.GetOrientationAttr().Get(), UsdGeom.Tokens.rightHanded)
            normals_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar(UsdGeom.Tokens.normals)
            self.assertTrue(normals_primvar.HasAuthoredValue())
            self.assertEqual(normals_primvar.GetInterpolation(), UsdGeom.Tokens.vertex)
            self.assertEqual(list(normals_primvar.Get()), [self.RIBBON_NORMAL])
            self.assertEqual(normals_primvar.GetIndices(), Vt.IntArray([0, 0, 0, 0, 0, 0, 0]))
            widths_primvar = UsdGeom.PrimvarsAPI(prim).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.16)

        # Check periodic wrap (linearPeriodicWrap, cubicPeriodicWrap)
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[12]]),
            UsdGeom.Tokens.linear,
            UsdGeom.Tokens.periodic,
        )
        self._checkBasisCurvesPrim(
            stage.GetPrimAtPath(name_to_path[curve_prim_names[13]]),
            UsdGeom.Tokens.cubic,
            UsdGeom.Tokens.periodic,
        )
        for index in (12, 13):
            typed_prim = UsdGeom.BasisCurves(stage.GetPrimAtPath(name_to_path[curve_prim_names[index]]))
            self.assertEqual(typed_prim.GetCurveVertexCountsAttr().Get(), Vt.IntArray([6]))
            widths_primvar = UsdGeom.PrimvarsAPI(typed_prim.GetPrim()).GetPrimvar(UsdGeom.Tokens.widths)
            self.assertTrue(widths_primvar.HasAuthoredValue())
            self.assertEqual(widths_primvar.GetInterpolation(), UsdGeom.Tokens.constant)
            self.assertAlmostEqual(widths_primvar.Get()[0], 0.12)

        # Check local Z translation for the periodic pair (linear below, cubic above)
        translation, _, _, _, _ = usdex.core.getLocalTransformComponents(stage.GetPrimAtPath(name_to_path[curve_prim_names[12]]))
        self.assertAlmostEqual(translation[2], -1.1, places=3)
        translation, _, _, _, _ = usdex.core.getLocalTransformComponents(stage.GetPrimAtPath(name_to_path[curve_prim_names[13]]))
        self.assertAlmostEqual(translation[2], 1.1, places=3)

        # Check local Z translation for the first three pairs (linear below, cubic above)
        for index, expected_z in ((0, -1.1), (1, 0.3), (2, -1.1), (3, 0.3), (4, -1.1), (5, 0.3)):
            translation, pivot, rotation, rotation_order, scale = usdex.core.getLocalTransformComponents(
                stage.GetPrimAtPath(name_to_path[curve_prim_names[index]])
            )
            self.assertAlmostEqual(translation[2], expected_z, places=3)

        stage = None

    def runSampleOptions(self, script, programPath):
        with tempfile.TemporaryDirectory() as tempDirStr:
            tempDir = pathlib.Path(tempDirStr)
            argsRuns = [
                (pathlib.Path(tempDir / "test_stage.usdc").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage.usda").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_binary.usd").as_posix(), None),
                (pathlib.Path(tempDir / "test_stage_text.usd").as_posix(), "--usda"),
            ]
            curves_xform_names = ["curvesXform", "curvesXform_1"]

            for args in argsRuns:
                for idx in range(len(curves_xform_names)):
                    if args[1]:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0], args[1])
                    else:
                        return_code, output = utils.shell.run_shell_script(script, programPath, "-p", args[0])
                    self.assertEqual(return_code, 0, output)
                    self._checkStageContents(args[0], curves_xform_names[idx], self.CURVE_NAMES)
                    utils.fileFormat.checkLayerFormat(self, args[0], args[1])

            # Test invalid options
            return_code, output = utils.shell.run_shell_script(script, programPath, "-p", pathlib.Path(tempDir / "test_stage.usdc").as_posix(), "-a")
            self.assertEqual(return_code, 2)
