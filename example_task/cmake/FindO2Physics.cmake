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

set(O2Physics_FOUND FALSE)

if(O2PHYSICS_ROOT)

  # Check if O2Physics is really installed there
  if(EXISTS ${O2PHYSICS_ROOT}/bin
     AND EXISTS ${O2PHYSICS_ROOT}/lib
     AND EXISTS ${O2PHYSICS_ROOT}/include)

     include(O2PhysicsDefineOptions)
     o2physics_define_options()

     include(O2PhysicsDefineOutputPaths)
     o2physics_define_output_paths()

     include(O2PhysicsDefineRPATH)
     o2physics_define_rpath()

     # External dependencies
     include(dependencies/CMakeLists.txt)

     # Include macros
    include(O2PhysicsNameTarget)
    include(O2PhysicsAddExecutable)
    include(O2PhysicsAddWorkflow)
    include(O2PhysicsAddLibrary)
    include(O2PhysicsAddHeaderOnlyLibrary)
    include(O2PhysicsTargetRootDictionary)

    include_directories("${CMAKE_CURRENT_SOURCE_DIR}")


    # TODO this is really not the way it should be done
    include_directories(${O2PHYSICS_ROOT}/include)
    # TODO neither is this
    link_directories(${O2PHYSICS_ROOT}/lib)

    set(O2Physics_FOUND TRUE)

    message(STATUS "O2Physics ... - found ${O2PHYSICS_ROOT}")

  else()

    message(STATUS "O2Physics ... - not found")

  endif()
endif(O2PHYSICS_ROOT)
