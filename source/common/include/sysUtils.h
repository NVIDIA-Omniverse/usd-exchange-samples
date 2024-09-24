// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//


#pragma once

#include <fmt/format.h>

#include <pxr/base/arch/env.h>
#if defined(ARCH_OS_WINDOWS)
#pragma warning(push)
#pragma warning(disable : 4245) // 'initializing': conversion from 'int' to 'size_t'
#include <pxr/base/arch/fileSystem.h>
#pragma warning(pop)
#else
#include <pxr/base/arch/fileSystem.h>
#endif
#include <pxr/base/arch/systemInfo.h>
#include <pxr/base/tf/stringUtils.h>

#include <filesystem>
#include <iostream>
#include <string>


namespace samples
{

//! Get the default USD stage path
//!
//! This function uses the OpenUSD file system utility to find the user's temp directory and
//! construct a string representing the sample's default USD stage path
//!
//! @param extension The file extension to use for the USD stage (.usdc, .usda, .usd)
//!
//! @returns An absolute, default USD stage path
std::string getDefaultStagePath(const char* extension)
{
    std::string tempDir = pxr::ArchNormPath(pxr::ArchGetTmpDir());
    return fmt::format("{0}/usdex/sample{1}", tempDir, extension);
}


//! Copies a texture file to the stage path's "textures" subdirectory
//!
//! The samples have light and material textures in the /resources/Materials directory.
//! These are copied by this function to be near the stage on disk.
//!
//! @param stagePath The absolute path to the stage
//! @param textureFile The texture to copy
//!
//! @returns The relative texture path for the asset attribute
std::string copyTextureToStagePath(const std::string& stagePath, const std::string& textureFile)
{
    // Copy the HDRI texture to the stage path "textures" subdirectory
    const std::string texturesSubDir("textures");
    std::string textureSourcePath(fmt::format("{0}../../../resources/Materials/{1}", pxr::TfGetPathName(pxr::ArchGetExecutablePath()), textureFile));
    std::string stagePathParent(pxr::TfGetPathName(stagePath));
    std::string textureTargetPath;

    // Make a textures directory in the same dir as the root stage. This requires a special case when the stage has no "parent"
    std::error_code ec;
    if (stagePathParent.empty())
    {
        textureTargetPath = fmt::format("{0}/{1}", texturesSubDir, textureFile);
    }
    else
    {
        textureTargetPath = fmt::format("{0}/{1}/{2}", stagePathParent, texturesSubDir, textureFile);
    }

    std::filesystem::create_directories(std::filesystem::path(textureTargetPath).parent_path(), ec);
    if (ec)
    {
        std::cout << "Error creating directories: " << ec.message() << std::endl;
    }
    std::filesystem::copy(textureSourcePath, textureTargetPath, std::filesystem::copy_options::update_existing, ec);
    if (ec)
    {
        std::cout << "Error copying file: " << ec.message() << std::endl;
    }
    return fmt::format("./{0}/{1}", texturesSubDir, textureFile);
}

} // namespace samples
