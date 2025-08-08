# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

# This makefile is a simple example for an application, or converter for including, linking, and executing with
# OpenUSD and the OpenUSD Exchange SDK
#
# By default it will build against the release version of OpenUSD, to build against the debug version run `make CONFIG=debug`.

# The expectation is that OpenUSD, the OpenUSD Exchange SDK, and other dependencies are present in the `$project_root/usdex/target-deps` directory
DEPSDIR = $(CURDIR)/usdex/target-deps
PYTHONVER = python3.10
PROGRAMNAME = UsdTraverse

ifndef CONFIG
	CONFIG=release
endif

ifndef TARGETDIR
	TARGETDIR = $(CURDIR)/$(CONFIG)
endif

# Debug vs. Release differences
ifeq ($(CONFIG),debug)
	CONFIG_DEFINES += -g -DDEBUG -O0 -DTBB_USE_DEBUG=1
else ifeq ($(CONFIG),release)
	CONFIG_DEFINES += -DNDEBUG -O2
endif

# ABI Settings
ifndef ABI_DEFINES
	ABI_DEFINES = -D_GLIBCXX_USE_CXX11_ABI=1 -std=c++17
endif

# Ignored Warnings
ifndef IGNORED_WARNINGS
	IGNORED_WARNINGS = -Wno-deprecated -DTBB_SUPPRESS_DEPRECATED_MESSAGES
endif

# Include search directories
USDEX_INCLUDE_DIRS = \
 -isystem $(DEPSDIR)/usd-exchange/$(CONFIG)/include \
 -isystem $(DEPSDIR)/usd/$(CONFIG)/include

# USD libs (most of these not required, but this is a proper set for a fully featured converter)
USD_LIBS = \
 -lusd_ar \
 -lusd_arch \
 -lusd_gf \
 -lusd_js \
 -lusd_kind \
 -lusd_pcp \
 -lusd_plug \
 -lusd_sdf \
 -lusd_tf \
 -lusd_trace \
 -lusd_usd \
 -lusd_usdGeom \
 -lusd_usdLux \
 -lusd_usdPhysics \
 -lusd_usdShade \
 -lusd_usdUtils \
 -lusd_vt \
 -lusd_work

# For USD 24.11 and newer
USD_LIBS += \
 -lusd_python \
 -lusd_ts

# For USD 24.08 and older, uncomment and remove the block above.
# USDEX_INCLUDE_DIRS += \
#  -isystem $(DEPSDIR)/usd/$(CONFIG)/include/boost-1_78
# USD_LIBS += \
#  -lboost_python310

USDEX_LIBS = \
 -lusdex_core

# Library dependency directories
USDEX_LIB_DIRS = \
 -L$(DEPSDIR)/usd-exchange/$(CONFIG)/lib \
 -L$(DEPSDIR)/usd/$(CONFIG)/lib

# Python specifics
ifndef PYTHON_INCLUDE_DIR
	PYTHON_INCLUDE_DIR = -isystem $(DEPSDIR)/python/include/$(PYTHONVER)
endif

ifndef PYTHON_LIB
	PYTHON_LIB = -l$(PYTHONVER)
endif

ifndef PYTHON_LIB_DIR
	PYTHON_LIB_DIR = -L$(DEPSDIR)/python/lib
endif

# Common flags
CXXFLAGS += $(CONFIG_DEFINES) $(ABI_DEFINES) $(IGNORED_WARNINGS) -m64
INCLUDES += $(USDEX_INCLUDE_DIRS) $(PYTHON_INCLUDE_DIR)
LIBS += $(USD_LIBS) $(USDEX_LIBS) $(PYTHON_LIB)
LDFLAGS += $(USDEX_LIB_DIRS) $(PYTHON_LIB_DIR)

OBJS = $(TARGETDIR)/$(PROGRAMNAME).o

# Build Targets

all: $(TARGETDIR)/$(PROGRAMNAME)

# $@ matches the target; $< matches the first dependent
$(TARGETDIR)/$(PROGRAMNAME): $(OBJS)
	echo Linking $(PROGRAMNAME)
	g++ -o $@ $< $(LDFLAGS) $(LIBS)

$(OBJS): $(PROGRAMNAME).cpp | $(TARGETDIR)
	g++ $(INCLUDES) $(CXXFLAGS) -c $< -o $@

$(TARGETDIR):
	@echo Creating $(TARGETDIR)
	@mkdir -p $(TARGETDIR)

clean:
	rm -rf $(TARGETDIR)
