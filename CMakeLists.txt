# Copyright 2019-2020 CERN and copyright holders of ALICE O2.
# See https://alice-o2.web.cern.ch/copyright for details of the copyright holders.
# All rights not expressly granted are reserved.
#
# This software is distributed under the terms of the GNU General Public
# License v3 (GPL Version 3), copied verbatim in the file "COPYING".
#
# In applying this license CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

cmake_minimum_required(VERSION 3.17 FATAL_ERROR)

project(O2openaccess
        VERSION 0.0.1
        LANGUAGES CXX C
        DESCRIPTION "ALICE open access software")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
set_property(GLOBAL PROPERTY REPORT_UNDEFINED_PROPERTIES)

include(GNUInstallDirs)

cmake_host_system_information(RESULT _totalmem QUERY TOTAL_PHYSICAL_MEMORY)
math(EXPR _total_analysis_jobs "(${_totalmem}-4096)/4096")
if(_total_analysis_jobs LESS_EQUAL 0)
  set(_total_analysis_jobs 1)
endif()
set(ANALYSIS_COMPILE_POOL ${_total_analysis_jobs} CACHE STRING "How many parallel analysis compilation jobs")
set_property(GLOBAL PROPERTY JOB_POOLS analysis=${ANALYSIS_COMPILE_POOL})
message(STATUS "Limiting workflow compilations in parallel to: ${ANALYSIS_COMPILE_POOL}")

# C++ standard
if(NOT DEFINED CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
endif()

# Dependencies
find_package(O2 CONFIG REQUIRED)
find_package(O2Physics CONFIG REQUIRED)

include(O2PhysicsDefineOptions)
o2physics_define_options()

include(O2PhysicsDefineOutputPaths)
o2physics_define_output_paths()

include(O2PhysicsDefineRPATH)
o2physics_define_rpath()

# Include macros
include(O2PhysicsNameTarget)
include(O2PhysicsAddExecutable)
include(O2PhysicsAddWorkflow)
include(O2PhysicsAddLibrary)
include(O2PhysicsAddHeaderOnlyLibrary)
include(O2PhysicsTargetRootDictionary)

include_directories("${CMAKE_CURRENT_SOURCE_DIR}")

# Main targets of the project in various subdirectories. Order matters.
add_subdirectory(src)
