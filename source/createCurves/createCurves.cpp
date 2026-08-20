// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/Core.h>
#include <usdex/core/CurvesAlgo.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/gf/transform.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/basisCurves.h>
#include <pxr/usd/usdGeom/tokens.h>

#include <iostream>
#include <string>
#include <vector>


namespace
{

// World-space center of the curve gallery; all curve translations in kPlacements are relative to curvesXform
const pxr::GfVec3d kGalleryCenter(-6.3, 9.0, 2.0);

// Open curves use a single curve with seven control vertices
pxr::VtIntArray openCurveVertexCounts()
{
    return pxr::VtIntArray{ 7 };
}

// Control points for linear open curves
pxr::VtVec3fArray linearOpenPoints()
{
    return pxr::VtVec3fArray{
        pxr::GfVec3f(0.0f, 0.0f, 0.0f),    pxr::GfVec3f(0.267f, 0.0f, 0.3f), pxr::GfVec3f(0.53f, 0.0f, 0.2f), pxr::GfVec3f(0.9f, 0.0f, 0.0f),
        pxr::GfVec3f(1.356f, 0.0f, 0.15f), pxr::GfVec3f(1.844f, 0.0f, 0.5f), pxr::GfVec3f(2.4f, 0.0f, 0.45f),
    };
}

// Control points for cubic open curves (bezier basis)
pxr::VtVec3fArray cubicOpenPoints()
{
    return pxr::VtVec3fArray{
        pxr::GfVec3f(0.0f, 0.0f, 0.0f),    pxr::GfVec3f(0.3f, 0.0f, 0.6f), pxr::GfVec3f(0.45f, 0.0f, 0.15f), pxr::GfVec3f(0.9f, 0.0f, 0.0f),
        pxr::GfVec3f(1.35f, 0.0f, -0.15f), pxr::GfVec3f(1.8f, 0.0f, 0.9f), pxr::GfVec3f(2.4f, 0.0f, 0.45f),
    };
}

// Batched curves pack multiple independent curves into a single UsdGeomBasisCurves prim
pxr::VtIntArray batchedLinearCurveVertexCounts()
{
    return pxr::VtIntArray{ 7, 5 };
}

pxr::VtIntArray batchedCubicCurveVertexCounts()
{
    return pxr::VtIntArray{ 7, 4 };
}

// Control points for batched linear curves (7 + 5 vertices); second curve offset 0.3 m below the first
pxr::VtVec3fArray batchedLinearPoints()
{
    return pxr::VtVec3fArray{
        pxr::GfVec3f(0.0f, 0.0f, 0.0f),    pxr::GfVec3f(0.267f, 0.0f, 0.3f), pxr::GfVec3f(0.53f, 0.0f, 0.2f), pxr::GfVec3f(0.9f, 0.0f, 0.0f),
        pxr::GfVec3f(1.356f, 0.0f, 0.15f), pxr::GfVec3f(1.844f, 0.0f, 0.5f), pxr::GfVec3f(2.4f, 0.0f, 0.45f), pxr::GfVec3f(0.0f, 0.0f, -0.3f),
        pxr::GfVec3f(0.267f, 0.0f, 0.0f),  pxr::GfVec3f(0.53f, 0.0f, -0.1f), pxr::GfVec3f(0.9f, 0.0f, -0.3f), pxr::GfVec3f(1.356f, 0.0f, -0.15f),
    };
}

// Control points for batched cubic curves (7 + 4 vertices); second curve is one bezier segment below the first
pxr::VtVec3fArray batchedCubicPoints()
{
    return pxr::VtVec3fArray{
        pxr::GfVec3f(0.0f, 0.0f, 0.0f),    pxr::GfVec3f(0.3f, 0.0f, 0.6f),    pxr::GfVec3f(0.45f, 0.0f, 0.15f), pxr::GfVec3f(0.9f, 0.0f, 0.0f),
        pxr::GfVec3f(1.35f, 0.0f, -0.15f), pxr::GfVec3f(1.8f, 0.0f, 0.9f),    pxr::GfVec3f(2.4f, 0.0f, 0.45f),  pxr::GfVec3f(0.0f, 0.0f, -0.3f),
        pxr::GfVec3f(0.3f, 0.0f, 0.3f),    pxr::GfVec3f(0.45f, 0.0f, -0.15f), pxr::GfVec3f(0.9f, 0.0f, -0.3f),
    };
}

// Periodic wrap curves use a single closed curve with six control vertices
pxr::VtIntArray periodicCurveVertexCounts()
{
    return pxr::VtIntArray{ 6 };
}

// Control points for periodic wrap curves (hexagonal loop)
pxr::VtVec3fArray periodicPoints()
{
    return pxr::VtVec3fArray{
        pxr::GfVec3f(0.0f, 0.0f, 0.5f),  pxr::GfVec3f(0.8f, 0.0f, 1.0f),  pxr::GfVec3f(1.6f, 0.0f, 0.5f),
        pxr::GfVec3f(1.6f, 0.0f, -0.5f), pxr::GfVec3f(0.8f, 0.0f, -1.0f), pxr::GfVec3f(0.0f, 0.0f, -0.5f),
    };
}

// FloatPrimvarData helpers for curve widths
usdex::core::FloatPrimvarData constantWidth(float width)
{
    return usdex::core::FloatPrimvarData(pxr::UsdGeomTokens->constant, pxr::VtFloatArray{ width });
}

usdex::core::FloatPrimvarData vertexWidths()
{
    return usdex::core::FloatPrimvarData(pxr::UsdGeomTokens->vertex, pxr::VtFloatArray{ 0.02f, 0.04f, 0.06f, 0.08f, 0.10f, 0.14f, 0.16f });
}

// FloatPrimvarData helpers for displayColor primvars
usdex::core::Vec3fPrimvarData constantDisplayColor()
{
    return usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->constant, pxr::VtVec3fArray{ pxr::GfVec3f(1.0f, 0.5f, 0.2f) });
}

usdex::core::Vec3fPrimvarData vertexDisplayColors()
{
    return usdex::core::Vec3fPrimvarData(
        pxr::UsdGeomTokens->vertex,
        pxr::VtVec3fArray{
            pxr::GfVec3f(1.0f, 0.0f, 0.0f),
            pxr::GfVec3f(1.0f, 0.5f, 0.0f),
            pxr::GfVec3f(1.0f, 1.0f, 0.0f),
            pxr::GfVec3f(0.0f, 1.0f, 0.0f),
            pxr::GfVec3f(0.0f, 1.0f, 1.0f),
            pxr::GfVec3f(0.0f, 0.0f, 1.0f),
            pxr::GfVec3f(0.5f, 0.0f, 1.0f),
        }
    );
}

usdex::core::FloatPrimvarData vertexDisplayOpacities()
{
    return usdex::core::FloatPrimvarData(pxr::UsdGeomTokens->vertex, pxr::VtFloatArray{ 1.0f, 0.83f, 0.67f, 0.50f, 0.33f, 0.17f, 0.0f });
}

// Indexed vertex normals for oriented ribbon curves
usdex::core::Vec3fPrimvarData ribbonNormals(size_t count)
{
    pxr::VtVec3fArray normals(count, pxr::GfVec3f(0.0f, -1.0f, 0.0f));
    return usdex::core::Vec3fPrimvarData(pxr::UsdGeomTokens->vertex, normals);
}

// Maps a linear/cubic curve pair to local translations under curvesXform
struct CurvePairPlacement
{
    size_t linearIndex;
    size_t cubicIndex;
    pxr::GfVec3d linearTranslation;
    pxr::GfVec3d cubicTranslation;
};

// Seven vertically stacked pairs; linear below, cubic above
const CurvePairPlacement kPlacements[] = {
    { 0, 1, pxr::GfVec3d(-3.2, 1.0, -1.1), pxr::GfVec3d(-3.2, 1.0, 0.3) },     { 2, 3, pxr::GfVec3d(-1.2, 1.0, -1.1), pxr::GfVec3d(-1.2, 1.0, 0.3) },
    { 4, 5, pxr::GfVec3d(0.8, 1.0, -1.1), pxr::GfVec3d(0.8, 1.0, 0.3) },       { 6, 7, pxr::GfVec3d(-3.2, 0.0, -1.1), pxr::GfVec3d(-3.2, 0.0, 0.3) },
    { 8, 9, pxr::GfVec3d(-1.2, 0.0, -1.1), pxr::GfVec3d(-1.2, 0.0, 0.3) },     { 10, 11, pxr::GfVec3d(0.8, 0.0, -1.1), pxr::GfVec3d(0.8, 0.0, 0.3) },
    { 12, 13, pxr::GfVec3d(-1.2, -1.0, -1.1), pxr::GfVec3d(-1.2, -1.0, 1.1) },
};

//! Set the local translation of a curve prim under curvesXform
void setCurveTranslation(const pxr::UsdGeomBasisCurves& curves, const pxr::GfVec3d& translation)
{
    usdex::core::setLocalTransform(
        curves, /* xformable */
        translation, /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(0.0f), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1.0f) /* scale */
    );
}

//! Create fourteen UsdGeomBasisCurves prims in seven feature-comparison pairs
//!
//! Each pair demonstrates the same curve feature with linear (below) and cubic (above) types:
//! batched multi-curve, constant width, per-vertex width, display color, per-vertex display color,
//! oriented ribbon, and periodic wrap.
//!
//! @param defaultPrim The stage default prim (typically "World")
//!
//! @returns true if all curves were created successfully
bool createCurveGallery(pxr::UsdPrim defaultPrim)
{
    // Desired child prim names for the fourteen curve prims
    const std::vector<std::string> curveNames = {
        "linearBatched",    "cubicBatched",       "linearUniformWidth", "cubicUniformWidth",        "linearVertexWidth",
        "cubicVertexWidth", "linearDisplayColor", "cubicDisplayColor",  "linearVertexDisplayColor", "cubicVertexDisplayColor",
        "linearRibbon",     "cubicRibbon",        "linearPeriodicWrap", "cubicPeriodicWrap",
    };

    const pxr::VtIntArray openCounts = openCurveVertexCounts();
    const pxr::VtVec3fArray linearOpen = linearOpenPoints();
    const pxr::VtVec3fArray cubicOpen = cubicOpenPoints();
    const pxr::VtIntArray batchedLinearCounts = batchedLinearCurveVertexCounts();
    const pxr::VtIntArray batchedCubicCounts = batchedCubicCurveVertexCounts();
    const pxr::VtVec3fArray batchedLinear = batchedLinearPoints();
    const pxr::VtVec3fArray batchedCubic = batchedCubicPoints();
    const pxr::VtIntArray periodicCounts = periodicCurveVertexCounts();
    const pxr::VtVec3fArray periodic = periodicPoints();

    // Parent Xform for the gallery; placed at the hardcoded world-space center
    const pxr::TfToken curvesXformToken = usdex::core::getValidChildName(defaultPrim, "curvesXform");
    pxr::GfTransform curvesXformTransform;
    curvesXformTransform.SetTranslation(kGalleryCenter);
    pxr::UsdGeomXform curvesXformPrim = usdex::core::defineXform(defaultPrim, curvesXformToken, curvesXformTransform);
    if (!curvesXformPrim)
    {
        return false;
    }
    const pxr::UsdPrim curveParent = curvesXformPrim.GetPrim();

    // Get valid, unique child prim names for all curve prims under curvesXform
    const pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(curveParent, curveNames);

    // Reusable primvar data shared across curve pairs
    const usdex::core::FloatPrimvarData uniformWidth = constantWidth(0.12f);
    const usdex::core::FloatPrimvarData ribbonWidth = constantWidth(0.16f);
    const usdex::core::FloatPrimvarData periodicWidth = constantWidth(0.12f);
    const usdex::core::FloatPrimvarData vertexWidth = vertexWidths();
    const usdex::core::Vec3fPrimvarData displayColor = constantDisplayColor();
    const usdex::core::Vec3fPrimvarData vertexDisplayColor = vertexDisplayColors();
    const usdex::core::FloatPrimvarData vertexDisplayOpacity = vertexDisplayOpacities();
    usdex::core::Vec3fPrimvarData ribbonNormals = ::ribbonNormals(linearOpen.size());
    ribbonNormals.index(); // share one normal value, (0, -1, 0), across all vertices

    for (const CurvePairPlacement& placement : kPlacements)
    {
        if (placement.linearIndex == 12)
        {
            // Periodic wrap (closed loop)
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                periodicCounts,
                periodic,
                pxr::UsdGeomTokens->periodic,
                periodicWidth
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                periodicCounts,
                periodic,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->periodic,
                periodicWidth
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        if (placement.linearIndex == 10)
        {
            // Oriented ribbon (indexed normals + constant width)
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                openCounts,
                linearOpen,
                pxr::UsdGeomTokens->nonperiodic,
                ribbonWidth,
                ribbonNormals
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                openCounts,
                cubicOpen,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->nonperiodic,
                ribbonWidth,
                ribbonNormals
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        if (placement.linearIndex == 8)
        {
            // Per-vertex display color and opacity (with constant width)
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                openCounts,
                linearOpen,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth,
                std::nullopt,
                vertexDisplayColor,
                vertexDisplayOpacity
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                openCounts,
                cubicOpen,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth,
                std::nullopt,
                vertexDisplayColor,
                vertexDisplayOpacity
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        if (placement.linearIndex == 6)
        {
            // Constant display color (with constant width)
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                openCounts,
                linearOpen,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth,
                std::nullopt,
                displayColor
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                openCounts,
                cubicOpen,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth,
                std::nullopt,
                displayColor
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        if (placement.linearIndex == 4)
        {
            // Per-vertex width
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                openCounts,
                linearOpen,
                pxr::UsdGeomTokens->nonperiodic,
                vertexWidth
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                openCounts,
                cubicOpen,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->nonperiodic,
                vertexWidth
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        if (placement.linearIndex == 2)
        {
            // Constant width
            pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
                curveParent,
                validTokens[placement.linearIndex].GetString(),
                openCounts,
                linearOpen,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth
            );
            if (!linearCurves)
            {
                return false;
            }
            setCurveTranslation(linearCurves, placement.linearTranslation);

            pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
                curveParent,
                validTokens[placement.cubicIndex].GetString(),
                openCounts,
                cubicOpen,
                pxr::UsdGeomTokens->bezier,
                pxr::UsdGeomTokens->nonperiodic,
                uniformWidth
            );
            if (!cubicCurves)
            {
                return false;
            }
            setCurveTranslation(cubicCurves, placement.cubicTranslation);
            continue;
        }

        // Batched multi-curve (two curves per prim, constant width)
        pxr::UsdGeomBasisCurves linearCurves = usdex::core::defineLinearBasisCurves(
            curveParent,
            validTokens[placement.linearIndex].GetString(),
            batchedLinearCounts,
            batchedLinear,
            pxr::UsdGeomTokens->nonperiodic,
            uniformWidth
        );
        if (!linearCurves)
        {
            return false;
        }
        setCurveTranslation(linearCurves, placement.linearTranslation);

        pxr::UsdGeomBasisCurves cubicCurves = usdex::core::defineCubicBasisCurves(
            curveParent,
            validTokens[placement.cubicIndex].GetString(),
            batchedCubicCounts,
            batchedCubic,
            pxr::UsdGeomTokens->bezier,
            pxr::UsdGeomTokens->nonperiodic,
            uniformWidth
        );
        if (!cubicCurves)
        {
            return false;
        }
        setCurveTranslation(cubicCurves, placement.cubicTranslation);
    }

    return true;
}

} // namespace


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createCurves", "Creates curves using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    if (!createCurveGallery(stage->GetDefaultPrim()))
    {
        std::cout << "Error creating curves, exiting" << std::endl;
        return -1;
    }

    // Save the stage to disk
    if (!samples::saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath))
    {
        return -1;
    }

    return 0;
}
