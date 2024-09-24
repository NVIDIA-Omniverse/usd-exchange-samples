// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
    // Put the telephoto camera about 3000 units from the origin and focus on the cube we created in createStage
    pxr::GfCamera gfCam = pxr::GfCamera(
        /* transform */ pxr::GfMatrix4d(1.0),
        /* projection */ pxr::GfCamera::Projection::Perspective,
        /* horizontalAperture */ static_cast<float>(pxr::GfCamera::DEFAULT_HORIZONTAL_APERTURE),
        /* verticalAperture */ static_cast<float>(pxr::GfCamera::DEFAULT_VERTICAL_APERTURE),
        /* horizontalApertureOffset */ 0.0f,
        /* verticalApertureOffset */ 0.0f,
        /* focalLength */ 100.0f,
        /* clippingRange */ pxr::GfRange1f(1, 1000000),
        /* clippingPlanes */ std::vector<pxr::GfVec4f>(),
        /* fStop */ 1.4f,
        /* focusDistance */ 3000.0f
    );

    // Define the camera
    pxr::UsdGeomCamera telephotoCamera = usdex::core::defineCamera(defaultPrim, validTokens[0], gfCam);

    // We could configure the xform in the GfCamera, but we can also do so with:
    usdex::core::setLocalTransform(
        telephotoCamera.GetPrim(), /* prim */
        pxr::GfVec3d(2531.459, 49.592, 1707.792), /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(-0.379f, 56.203f, 0.565f), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1.0f) /* scale */
    );

    // Put the wide-angle camera about 250 units from the origin and look towards the cube we created in createStage
    gfCam.SetFocusDistance(250.0f);
    gfCam.SetFocalLength(3.5f);
    gfCam.SetFStop(32.0f);

    // Define the camera
    pxr::UsdGeomCamera wideCamera = usdex::core::defineCamera(defaultPrim, validTokens[1], gfCam);

    // We could configure the xform in the GfCamera, but we can also do so with:
    usdex::core::setLocalTransform(
        wideCamera.GetPrim(), /* prim */
        pxr::GfVec3d(-283.657, 12.826, 140.9), /* translation */
        pxr::GfVec3d(0.0), /* pivot */
        pxr::GfVec3f(-1.234f, -64.0f, -2.53f), /* rotation */
        usdex::core::RotationOrder::eXyz, /* rotation order */
        pxr::GfVec3f(1.0f) /* scale */
    );

    // Save the stage to disk
    usdex::core::saveStage(stage, "OpenUSD Exchange Samples");

    return 0;
}
