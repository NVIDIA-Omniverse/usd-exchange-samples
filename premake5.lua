-- Shared build scripts from repo_build package
repo_build = require("omni/repo/build")
repo_build.root = os.getcwd()

-- Shared build scripts for use in data exchange programs
usdex_build = require(path.replaceextension(os.matchfiles("_build/target-deps/usd-exchange/*/dev/tools/premake/usdex_build.lua")[1], ""))

workspace "USD-Exchange-Samples"
    usdex_build.setup_workspace()

    -- override some usdex_build settings
    -- install exeutables and libraries in the main target_build_dir
    target_bin_dir = target_build_dir
    target_lib_dir = target_build_dir


function sample(projectName)
    project(projectName)

    includedirs { "source/common/include" }

    -- setup all paths, links, and carb dependencies to enable usdex_core
    usdex_build.use_cxxopts()
    usdex_build.use_usd({
        "arch",
        "gf",
        "kind",
        "pcp",
        "plug",
        "sdf",
        "tf",
        "usd",
        "usdGeom",
        "usdLux",
        "usdPhysics",
        "usdSemantics",
        "usdShade",
        "usdSkel",
        "usdUtils",
        "vt",
        "work"
    })
    usdex_build.use_usdex_core()
    usdex_build.use_usdex_rtx()

    filter { "system:windows" }
        -- This sets the working directory when debugging/running from Visual Studio
        debugdir "$(ProjectDir)..\\..\\.."
    filter { "system:linux" }
        links { "pthread", "stdc++fs" }
    filter {}

    usdex_build.executable({
        name = projectName,
        sources = { "source/"..projectName.."/**.*" },
    })
end

-- Read samples from allSamples.txt and call sample() for each
local allSamplesFile = io.open("allSamples.txt", "r")
if allSamplesFile then
    for line in allSamplesFile:lines() do
        local sampleName = line:match("^%s*(.-)%s*$") -- trim whitespace
        if sampleName and sampleName ~= "" then
            sample(sampleName)
        end
    end
    allSamplesFile:close()
else
    print("Warning: allSamples.txt not found, no samples will be built")
end
