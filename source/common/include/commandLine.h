// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//


#pragma once

#include "sysUtils.h"
#include "usdUtils.h"

#include <cxxopts.hpp>

#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usd/usdFileFormat.h>
#include <pxr/usd/usd/usdaFileFormat.h>

#include <algorithm> // std::equal
#include <cctype> // std::tolower
#include <filesystem>
#include <iostream>
#include <string>

namespace samples
{
struct Args
{
    std::string stagePath;
    pxr::SdfLayer::FileFormatArguments fileFormatArgs;
};

bool ichar_equals(char a, char b)
{
    return std::tolower(static_cast<unsigned char>(a)) == std::tolower(static_cast<unsigned char>(b));
}

bool iequals(const std::string& a, const std::string& b)
{
    return std::equal(a.begin(), a.end(), b.begin(), b.end(), ichar_equals);
}

Args parseCommonOptions(int argc, char* argv[], const char* sampleName, const char* sampleDesc)
{
    Args args;
    args.stagePath = samples::getDefaultStagePath(".usdc");

    // Handle command line arguments
    // clang-format off
    cxxopts::Options options(sampleName, sampleDesc);
    options.add_options()
        ("a,usda", "Output a text stage rather than binary", cxxopts::value<bool>()->default_value("false"))
        ("h,help", "Print usage")
        ("p,path", "Alternate destination stage path", cxxopts::value<std::string>()->default_value(args.stagePath))
        ;
    // clang-format on
    try
    {
        cxxopts::ParseResult result = options.parse(argc, argv);
        if (result.count("help"))
        {
            std::cout << options.help() << std::endl;
            exit(0);
        }
        // Stage path and format
        //  --path c:\folder\stage.usdc --usda -> error about invalid arg combo
        //  --path c:\folder\stage.usda --usda -> redundant but silent pass
        //  --path c:\folder\stage.usd --usda -> use file format args to steer the layer format
        if (result["usda"].as<bool>())
        {
            args.stagePath = samples::getDefaultStagePath(".usda");
        }
        if (result.count("path"))
        {
            args.stagePath = result["path"].as<std::string>();
            std::filesystem::path extension = std::filesystem::path(args.stagePath).extension();
            if (result["usda"].as<bool>() && iequals(extension.string(), ".usdc"))
            {
                std::cout << "Error parsing arguments: Inconsistent use of --usda with a .usdc stage" << std::endl;
                exit(2);
            }
            if (result["usda"].as<bool>() && iequals(extension.string(), ".usd"))
            {
                args.fileFormatArgs.insert({ pxr::UsdUsdFileFormatTokens->FormatArg, pxr::UsdUsdaFileFormatTokens->Id });
            }
        }
    }
    catch (const cxxopts::OptionException& e)
    {
        std::cout << "Error parsing options: " << e.what() << std::endl;
        std::cout << std::endl << options.help() << std::endl;
        exit(2);
    }
    return args;
}

} // namespace samples
