# SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Standalone CMake build for the OpenUSD Exchange SDK C++ samples. The build uses the SDK package from an
# install_usdex runtime. Set CMAKE_PREFIX_PATH to that package. Set the USDEX dependency roots for its OpenUSD,
# oneTBB, MaterialX, and Python installations.

cmake_minimum_required(VERSION 3.20)
project(usd-exchange-samples CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# emit the sample executables into bin/ (beside the assembled runtime DLLs on Windows); on Linux they self-locate
# the sibling lib/ via the $ORIGIN/../lib rpath
set(USDEX_SAMPLES_RUNTIME_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Root directory the sample runtime is assembled into")
# The empty generator expression prevents multi-config generators from appending Debug/Release after bin.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${USDEX_SAMPLES_RUNTIME_DIR}/bin$<0:>")
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)
set(CMAKE_INSTALL_RPATH "$ORIGIN;$ORIGIN/../lib")

find_package(usd-exchange REQUIRED)
find_path(SAMPLES_CXXOPTS_INCLUDE_DIR cxxopts.hpp REQUIRED)  # header-only CLI parser

# the OpenUSD modules the samples call directly (linked via the SDK's usdex_target_link_usd helper)
set(USDEX_SAMPLE_USD_LIBS arch gf kind pcp plug sdf tf usd usdGeom usdLux usdPhysics usdSemantics usdShade usdSkel usdUtils vt work)

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/allSamples.txt" _samples)
foreach(_sample ${_samples})
    string(STRIP "${_sample}" _sample)
    if(_sample STREQUAL "")
        continue()
    endif()
    file(GLOB _srcs CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/source/${_sample}/*.cpp")
    add_executable(${_sample} ${_srcs})
    target_include_directories(${_sample} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/source/common/include")
    # keep third-party headers SYSTEM so their warnings never surface in the samples build
    target_include_directories(${_sample} SYSTEM PRIVATE "${SAMPLES_CXXOPTS_INCLUDE_DIR}")
    target_link_libraries(${_sample} PRIVATE usdex::core usdex::rtx)
    usdex_target_link_usd(${_sample} ${USDEX_SAMPLE_USD_LIBS})
    if(UNIX AND NOT APPLE)
        target_link_libraries(${_sample} PRIVATE pthread stdc++fs)
    endif()
endforeach()
