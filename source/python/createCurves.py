# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import argparse
import sys

import common.commandLine
import common.usdUtils
import usdex.core
from pxr import Gf, UsdGeom, Vt

# World-space center of the curve gallery; curve translations in CURVE_PAIR_PLACEMENTS are relative to curvesXform
GALLERY_CENTER = Gf.Vec3d(-6.3, 9.0, 2.0)

# Open curves use a single curve with seven control vertices
OPEN_CURVE_VERTEX_COUNTS = Vt.IntArray([7])

# Control points for linear open curves
LINEAR_OPEN_POINTS = Vt.Vec3fArray(
    [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.267, 0.0, 0.3),
        Gf.Vec3f(0.53, 0.0, 0.2),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.356, 0.0, 0.15),
        Gf.Vec3f(1.844, 0.0, 0.5),
        Gf.Vec3f(2.4, 0.0, 0.45),
    ]
)

# Control points for cubic open curves (bezier basis)
CUBIC_OPEN_POINTS = Vt.Vec3fArray(
    [
        Gf.Vec3f(0.0, 0.0, 0.0),
        Gf.Vec3f(0.3, 0.0, 0.6),
        Gf.Vec3f(0.45, 0.0, 0.15),
        Gf.Vec3f(0.9, 0.0, 0.0),
        Gf.Vec3f(1.35, 0.0, -0.15),
        Gf.Vec3f(1.8, 0.0, 0.9),
        Gf.Vec3f(2.4, 0.0, 0.45),
    ]
)

# Batched curves pack multiple independent curves into a single UsdGeom.BasisCurves prim
BATCHED_LINEAR_CURVE_VERTEX_COUNTS = Vt.IntArray([7, 5])
BATCHED_CUBIC_CURVE_VERTEX_COUNTS = Vt.IntArray([7, 4])

# Control points for batched linear curves (7 + 5 vertices); second curve offset 0.3 m below the first
BATCHED_LINEAR_POINTS = Vt.Vec3fArray(
    [
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
)

# Control points for batched cubic curves (7 + 4 vertices); second curve is one bezier segment below the first
BATCHED_CUBIC_POINTS = Vt.Vec3fArray(
    [
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
)

# Periodic wrap curves use a single closed curve with six control vertices
PERIODIC_CURVE_VERTEX_COUNTS = Vt.IntArray([6])

# Control points for periodic wrap curves (hexagonal loop)
PERIODIC_POINTS = Vt.Vec3fArray(
    [
        Gf.Vec3f(0.0, 0.0, 0.5),
        Gf.Vec3f(0.8, 0.0, 1.0),
        Gf.Vec3f(1.6, 0.0, 0.5),
        Gf.Vec3f(1.6, 0.0, -0.5),
        Gf.Vec3f(0.8, 0.0, -1.0),
        Gf.Vec3f(0.0, 0.0, -0.5),
    ]
)

# Desired child prim names for the fourteen curve prims
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

# Seven vertically stacked pairs; (linear index, cubic index, linear translation, cubic translation)
CURVE_PAIR_PLACEMENTS = [
    (0, 1, Gf.Vec3d(-3.2, 1.0, -1.1), Gf.Vec3d(-3.2, 1.0, 0.3)),
    (2, 3, Gf.Vec3d(-1.2, 1.0, -1.1), Gf.Vec3d(-1.2, 1.0, 0.3)),
    (4, 5, Gf.Vec3d(0.8, 1.0, -1.1), Gf.Vec3d(0.8, 1.0, 0.3)),
    (6, 7, Gf.Vec3d(-3.2, 0.0, -1.1), Gf.Vec3d(-3.2, 0.0, 0.3)),
    (8, 9, Gf.Vec3d(-1.2, 0.0, -1.1), Gf.Vec3d(-1.2, 0.0, 0.3)),
    (10, 11, Gf.Vec3d(0.8, 0.0, -1.1), Gf.Vec3d(0.8, 0.0, 0.3)),
    (12, 13, Gf.Vec3d(-1.2, -1.0, -1.1), Gf.Vec3d(-1.2, -1.0, 1.1)),
]


def _constant_width(width: float) -> usdex.core.FloatPrimvarData:
    """FloatPrimvarData for a constant curve width."""
    return usdex.core.FloatPrimvarData(UsdGeom.Tokens.constant, Vt.FloatArray([width]))


def _vertex_widths() -> usdex.core.FloatPrimvarData:
    """FloatPrimvarData for per-vertex curve widths."""
    return usdex.core.FloatPrimvarData(
        UsdGeom.Tokens.vertex,
        Vt.FloatArray([0.02, 0.04, 0.06, 0.08, 0.1, 0.14, 0.16]),
    )


def _constant_display_color() -> usdex.core.Vec3fPrimvarData:
    """Vec3fPrimvarData for a constant displayColor primvar."""
    return usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.constant, Vt.Vec3fArray([Gf.Vec3f(1.0, 0.5, 0.2)]))


def _vertex_display_colors() -> usdex.core.Vec3fPrimvarData:
    """Vec3fPrimvarData for per-vertex displayColor primvars."""
    return usdex.core.Vec3fPrimvarData(
        UsdGeom.Tokens.vertex,
        Vt.Vec3fArray(
            [
                Gf.Vec3f(1.0, 0.0, 0.0),
                Gf.Vec3f(1.0, 0.5, 0.0),
                Gf.Vec3f(1.0, 1.0, 0.0),
                Gf.Vec3f(0.0, 1.0, 0.0),
                Gf.Vec3f(0.0, 1.0, 1.0),
                Gf.Vec3f(0.0, 0.0, 1.0),
                Gf.Vec3f(0.5, 0.0, 1.0),
            ]
        ),
    )


def _vertex_display_opacities() -> usdex.core.FloatPrimvarData:
    """FloatPrimvarData for per-vertex displayOpacity primvars from 1.0 to 0.0."""
    return usdex.core.FloatPrimvarData(
        UsdGeom.Tokens.vertex,
        Vt.FloatArray([1.0, 0.83, 0.67, 0.50, 0.33, 0.17, 0.0]),
    )


def _ribbon_normals(count: int) -> usdex.core.Vec3fPrimvarData:
    """Vec3fPrimvarData for indexed ribbon normals shared across all control points."""
    ribbon_normals = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.vertex, Vt.Vec3fArray([Gf.Vec3f(0.0, -1.0, 0.0)] * count))
    ribbon_normals.index()  # share one normal value, (0, -1, 0), across all vertices
    return ribbon_normals


def _set_curve_translation(curves, translation: Gf.Vec3d):
    """Set the local translation of a curve prim under curvesXform."""
    usdex.core.setLocalTransform(
        xformable=curves,
        translation=translation,
        pivot=Gf.Vec3d(0.0),
        rotation=Gf.Vec3f(0.0),
        rotationOrder=usdex.core.RotationOrder.eXyz,
        scale=Gf.Vec3f(1.0),
    )


def create_curve_gallery(default_prim):
    """
    Create fourteen UsdGeom.BasisCurves prims in seven feature-comparison pairs.

    Each pair demonstrates the same curve feature with linear (below) and cubic (above) types:
    batched multi-curve, constant width, per-vertex width, display color, per-vertex display color,
    oriented ribbon, and periodic wrap.

    Args:
        default_prim: The stage default prim (typically "World")

    Returns:
        True if all curves were created successfully
    """
    # Parent Xform for the gallery; placed at the hardcoded world-space center
    curves_xform_name = usdex.core.getValidChildName(default_prim, "curvesXform")
    curves_xform_prim = usdex.core.defineXform(
        parent=default_prim,
        name=curves_xform_name,
        transform=Gf.Transform(GALLERY_CENTER),
    )
    if not curves_xform_prim:
        return False
    curve_parent = curves_xform_prim.GetPrim()

    # Get valid, unique child prim names for all curve prims under curvesXform
    valid_tokens = usdex.core.getValidChildNames(curve_parent, CURVE_NAMES)

    # Reusable primvar data shared across curve pairs
    uniform_width = _constant_width(0.12)
    ribbon_width = _constant_width(0.16)
    periodic_width = _constant_width(0.12)
    vertex_width = _vertex_widths()
    display_color = _constant_display_color()
    vertex_display_color = _vertex_display_colors()
    vertex_display_opacity = _vertex_display_opacities()
    ribbon_normals = _ribbon_normals(len(LINEAR_OPEN_POINTS))

    for linear_index, cubic_index, linear_translation, cubic_translation in CURVE_PAIR_PLACEMENTS:
        linear_name = valid_tokens[linear_index]
        cubic_name = valid_tokens[cubic_index]

        if linear_index == 12:
            # Periodic wrap (closed loop)
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                PERIODIC_CURVE_VERTEX_COUNTS,
                PERIODIC_POINTS,
                wrap=UsdGeom.Tokens.periodic,
                widths=periodic_width,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                PERIODIC_CURVE_VERTEX_COUNTS,
                PERIODIC_POINTS,
                basis=UsdGeom.Tokens.bezier,
                wrap=UsdGeom.Tokens.periodic,
                widths=periodic_width,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        if linear_index == 10:
            # Oriented ribbon (indexed normals + constant width)
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                OPEN_CURVE_VERTEX_COUNTS,
                LINEAR_OPEN_POINTS,
                widths=ribbon_width,
                normals=ribbon_normals,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                OPEN_CURVE_VERTEX_COUNTS,
                CUBIC_OPEN_POINTS,
                basis=UsdGeom.Tokens.bezier,
                widths=ribbon_width,
                normals=ribbon_normals,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        if linear_index == 8:
            # Per-vertex display color and opacity (with constant width)
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                OPEN_CURVE_VERTEX_COUNTS,
                LINEAR_OPEN_POINTS,
                widths=uniform_width,
                displayColor=vertex_display_color,
                displayOpacity=vertex_display_opacity,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                OPEN_CURVE_VERTEX_COUNTS,
                CUBIC_OPEN_POINTS,
                basis=UsdGeom.Tokens.bezier,
                widths=uniform_width,
                displayColor=vertex_display_color,
                displayOpacity=vertex_display_opacity,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        if linear_index == 6:
            # Constant display color (with constant width)
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                OPEN_CURVE_VERTEX_COUNTS,
                LINEAR_OPEN_POINTS,
                widths=uniform_width,
                displayColor=display_color,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                OPEN_CURVE_VERTEX_COUNTS,
                CUBIC_OPEN_POINTS,
                basis=UsdGeom.Tokens.bezier,
                widths=uniform_width,
                displayColor=display_color,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        if linear_index == 4:
            # Per-vertex width
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                OPEN_CURVE_VERTEX_COUNTS,
                LINEAR_OPEN_POINTS,
                widths=vertex_width,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                OPEN_CURVE_VERTEX_COUNTS,
                CUBIC_OPEN_POINTS,
                basis=UsdGeom.Tokens.bezier,
                widths=vertex_width,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        if linear_index == 2:
            # Constant width
            linear_curves = usdex.core.defineLinearBasisCurves(
                curve_parent,
                linear_name,
                OPEN_CURVE_VERTEX_COUNTS,
                LINEAR_OPEN_POINTS,
                widths=uniform_width,
            )
            if not linear_curves:
                return False
            _set_curve_translation(linear_curves, linear_translation)

            cubic_curves = usdex.core.defineCubicBasisCurves(
                curve_parent,
                cubic_name,
                OPEN_CURVE_VERTEX_COUNTS,
                CUBIC_OPEN_POINTS,
                basis=UsdGeom.Tokens.bezier,
                widths=uniform_width,
            )
            if not cubic_curves:
                return False
            _set_curve_translation(cubic_curves, cubic_translation)
            continue

        # Batched multi-curve (two curves per prim, constant width)
        linear_curves = usdex.core.defineLinearBasisCurves(
            curve_parent,
            linear_name,
            BATCHED_LINEAR_CURVE_VERTEX_COUNTS,
            BATCHED_LINEAR_POINTS,
            widths=uniform_width,
        )
        if not linear_curves:
            return False
        _set_curve_translation(linear_curves, linear_translation)

        cubic_curves = usdex.core.defineCubicBasisCurves(
            curve_parent,
            cubic_name,
            BATCHED_CUBIC_CURVE_VERTEX_COUNTS,
            BATCHED_CUBIC_POINTS,
            basis=UsdGeom.Tokens.bezier,
            widths=uniform_width,
        )
        if not cubic_curves:
            return False
        _set_curve_translation(cubic_curves, cubic_translation)

    return True


def main(args):
    print(f"Stage path: {args.path}")

    stage = common.usdUtils.openOrCreateStage(identifier=args.path, fileFormatArgs=args.fileFormatArgs)
    if not stage:
        print("Error opening or creating stage, exiting")
        sys.exit(-1)

    if not create_curve_gallery(stage.GetDefaultPrim()):
        print("Error creating curves, exiting")
        sys.exit(-1)

    if not common.usdUtils.saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath):
        sys.exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates curves using the OpenUSD Exchange SDK", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    main(common.commandLine.parseCommonOptions(parser))
