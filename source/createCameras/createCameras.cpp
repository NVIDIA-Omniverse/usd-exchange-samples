// SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include "commandLine.h"
#include "sysUtils.h"
#include "usdUtils.h"

#include <usdex/core/CameraAlgo.h>
#include <usdex/core/Core.h>
#include <usdex/core/StageAlgo.h>
#include <usdex/core/XformAlgo.h>

#include <pxr/base/gf/camera.h>
#include <pxr/base/gf/transform.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/camera.h>

#include <iostream>
#include <vector>


int main(int argc, char* argv[])
{
    samples::Args args = samples::parseCommonOptions(argc, argv, "createCameras", "Creates cameras using the OpenUSD Exchange SDK");

    std::cout << "Stage path: " << args.stagePath << std::endl;

    pxr::UsdStageRefPtr stage = samples::openOrCreateStage(args.stagePath, "World", args.fileFormatArgs);
    if (!stage)
    {
        std::cout << "Error opening or creating stage, exiting" << std::endl;
        return -1;
    }

    pxr::UsdPrim defaultPrim = stage->GetDefaultPrim();

    // Get valid, unique child prim names for the two cameras under the default prim
    std::vector<std::string> cameraNames = std::vector<std::string>{ "telephotoCamera", "wideCamera" };
    pxr::TfTokenVector validTokens = usdex::core::getValidChildNames(defaultPrim, cameraNames);

    // GfCamera is a container for camera attributes, used by the Exchange SDK defineCamera function
    // Configure the telephoto camera with a long focus distance
    // Lens and filmback values are expressed in tenths of a scene unit, so the GfCamera defaults (sized for a
    // centimeter stage) and the focal length must be divided by 100 for this meter stage, otherwise the physical
    // lens aperture becomes meters wide and the render is heavily defocused
    pxr::GfCamera gfCam = pxr::GfCamera(
        /* transform */ pxr::GfMatrix4d(1.0),
        /* projection */ pxr::GfCamera::Projection::Perspective,
        /* horizontalAperture */ static_cast<float>(pxr::GfCamera::DEFAULT_HORIZONTAL_APERTURE / 100.0),
        /* verticalAperture */ static_cast<float>(pxr::GfCamera::DEFAULT_VERTICAL_APERTURE / 100.0),
        /* horizontalApertureOffset */ 0.0f,
        /* verticalApertureOffset */ 0.0f,
        /* focalLength */ 1.0f, // 100 mm
        /* clippingRange */ pxr::GfRange1f(0.01f, 10000.0f),
        /* clippingPlanes */ std::vector<pxr::GfVec4f>(),
        /* fStop */ 1.4f,
        /* focusDistance */ 88.62f
    );

    // Define the camera
    pxr::UsdGeomCamera telephotoCamera = usdex::core::defineCamera(defaultPrim, validTokens[0], gfCam);

    // We could configure the xform in the GfCamera, but we can also do so with:
    usdex::core::setLocalTransform(
        telephotoCamera, /* xformable */
        pxr::GfVec3d(65.71555, -58.62940, 14.15558), /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(81.474f, -0.314f, 47.484f), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1.0f) /* scale */
    );

    // Configure the wide-angle camera with a shorter focus distance
    gfCam.SetFocusDistance(5.63f);
    gfCam.SetFocalLength(0.035f); // 3.5 mm
    gfCam.SetFStop(32.0f);

    // Define the camera
    pxr::UsdGeomCamera wideCamera = usdex::core::defineCamera(defaultPrim, validTokens[1], gfCam);

    // We could configure the xform in the GfCamera, but we can also do so with:
    usdex::core::setLocalTransform(
        wideCamera, /* xformable */
        pxr::GfVec3d(-5.06538, -2.03795, 3.04977), /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(53.976f, 1.109f, -45.364f), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1.0f) /* scale */
    );

    // Save the stage to disk
    if (!samples::saveStage(stage, "OpenUSD Exchange Samples", args.usdzPath))
    {
        return -1;
    }

    return 0;
}
