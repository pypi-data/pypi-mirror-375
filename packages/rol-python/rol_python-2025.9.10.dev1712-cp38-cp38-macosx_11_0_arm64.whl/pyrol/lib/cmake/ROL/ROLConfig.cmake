# @HEADER
# *****************************************************************************
#            TriBITS: Tribal Build, Integrate, and Test System
#
# Copyright 2013-2016 NTESS and the TriBITS contributors.
# SPDX-License-Identifier: BSD-3-Clause
# *****************************************************************************
# @HEADER

##############################################################################
#
# CMake variable for use by Trilinos/ROL clients.
#
# Do not edit: This file was generated automatically by CMake.
#
##############################################################################

if(CMAKE_VERSION VERSION_LESS 3.3)
  set(${CMAKE_FIND_PACKAGE_NAME}_NOT_FOUND_MESSAGE
    "ROL requires CMake 3.3 or later for 'if (... IN_LIST ...)'"
    )
  set(${CMAKE_FIND_PACKAGE_NAME}_FOUND FALSE)
  return()
endif()
cmake_minimum_required(VERSION 3.3...3.23.0)

## ---------------------------------------------------------------------------
## Compilers used by Trilinos/ROL build
## ---------------------------------------------------------------------------

set(ROL_CXX_COMPILER "/Applications/Xcode_16.4.app/Contents/Developer/usr/bin/g++")

set(ROL_C_COMPILER "/Applications/Xcode_16.4.app/Contents/Developer/usr/bin/gcc")

set(ROL_Fortran_COMPILER "")
# Deprecated!
set(ROL_FORTRAN_COMPILER "") 


## ---------------------------------------------------------------------------
## Compiler flags used by Trilinos/ROL build
## ---------------------------------------------------------------------------

## Give the build type
set(ROL_CMAKE_BUILD_TYPE "RELEASE")

## Set compiler flags, including those determined by build type
set(ROL_CXX_FLAGS [[ -O3 -DNDEBUG]])

set(ROL_C_FLAGS [[ -O3 -DNDEBUG]])

set(ROL_Fortran_FLAGS [[ ]])
# Deprecated
set(ROL_FORTRAN_FLAGS [[ ]])

## Extra link flags (e.g., specification of fortran libraries)
set(ROL_EXTRA_LD_FLAGS [[]])

## This is the command-line entry used for setting rpaths. In a build
## with static libraries it will be empty.
set(ROL_SHARED_LIB_RPATH_COMMAND "-Wl,-rpath,/var/folders/x7/ch5v91h56_zbvbd1y2f600dm0000gn/T/tmph6wlxpi8/wheel/platlib/pyrol/lib")
set(ROL_BUILD_SHARED_LIBS "ON")

set(ROL_LINKER /Applications/Xcode_16.4.app/Contents/Developer/usr/bin/ld)
set(ROL_AR /usr/bin/ar)

## ---------------------------------------------------------------------------
## Set library specifications and paths
## ---------------------------------------------------------------------------

## Base install location (if not in the build tree)
set(ROL_INSTALL_DIR "/var/folders/x7/ch5v91h56_zbvbd1y2f600dm0000gn/T/tmph6wlxpi8/wheel/platlib/pyrol")

## List of package libraries
set(ROL_LIBRARIES ROL::all_libs)

## ---------------------------------------------------------------------------
## MPI specific variables
##   These variables are provided to make it easier to get the mpi libraries
##   and includes on systems that do not use the mpi wrappers for compiling
## ---------------------------------------------------------------------------

set(ROL_MPI_LIBRARIES "")
set(ROL_MPI_LIBRARY_DIRS "")
set(ROL_MPI_INCLUDE_DIRS "")
set(ROL_MPI_EXEC "")
set(ROL_MPI_EXEC_MAX_NUMPROCS "")
set(ROL_MPI_EXEC_NUMPROCS_FLAG "")

## ---------------------------------------------------------------------------
## Set useful general variables
## ---------------------------------------------------------------------------

# Enables/Disables for upstream package dependencies
set(ROL_ENABLE_Teuchos ON)
set(ROL_ENABLE_Boost OFF)
set(ROL_ENABLE_ArrayFireCPU OFF)
set(ROL_ENABLE_Eigen OFF)
set(ROL_ENABLE_pebbl OFF)

# Exported cache variables
set(ROL_ENABLE_DEBUG "OFF")
set(HAVE_ROL_DEBUG "OFF")
set(ROL_ENABLE_TIMERS "OFF")
set(ROL_TIMERS "OFF")
set(ROL_ENABLE_PYROL "ON")
set(ENABLE_PYBIND11_PYROL "ON")
set(ROL_ENABLE_PARAMETERLIST_VALIDATION "OFF")
set(ENABLE_PARAMETERLIST_VALIDATION "OFF")
set(PYROL_PIP_INSTALL "ON")
set(PYROL_SCIKIT "ON")
set(PYROL_ENABLE_BINDER "OFF")
set(PYROL_GENERATE_SRC "OFF")
set(PYROL_BINDER_SUPPRESS_ERRORS "OFF")
set(PYROL_SUPPRESS_ERRORS "OFF")
set(PYROL_BINDER_USE_ONE_FILE "OFF")
set(PYROL_USE_ONE_FILE "OFF")
set(PYROL_BINDER_CMAKE_ERROR "ON")
set(PYROL_CMAKE_ERROR "ON")
set(PYROL_BINDER_VERBOSE "OFF")
set(PYROL_B_VERBOSE "OFF")
set(PYROL_ENABLE_BINDER_UPDATE "OFF")
set(PYROL_UPDATE_GENERATED_SRC "OFF")

# Include configuration of dependent packages
if (NOT TARGET Teuchos::all_libs)
  include("${CMAKE_CURRENT_LIST_DIR}/../Teuchos/TeuchosConfig.cmake")
endif()

# Import ROL targets
include("${CMAKE_CURRENT_LIST_DIR}/ROLTargets.cmake")

# Standard TriBITS-compliant external package variables
set(ROL_IS_TRIBITS_COMPLIANT TRUE)
set(ROL_TRIBITS_COMPLIANT_PACKAGE_CONFIG_FILE "${CMAKE_CURRENT_LIST_FILE}")
set(ROL_TRIBITS_COMPLIANT_PACKAGE_CONFIG_FILE_DIR "${CMAKE_CURRENT_LIST_DIR}")


## ----------------------------------------------------------------------------
## Create deprecated non-namespaced library targets for backwards compatibility
## ----------------------------------------------------------------------------

set(ROL_EXPORTED_PACKAGE_LIBS_NAMES "rol")

foreach(libname IN LISTS ROL_EXPORTED_PACKAGE_LIBS_NAMES)
  if (NOT TARGET ${libname})
    add_library(${libname} INTERFACE IMPORTED)
    target_link_libraries(${libname}
       INTERFACE ROL::${libname})
    set(deprecationMessage
      "WARNING: The non-namespaced target '${libname}' is deprecated!"
      "  If always using newer versions of the project 'Trilinos', then use the"
      " new namespaced target 'ROL::${libname}', or better yet,"
      " 'ROL::all_libs' to be less sensitive to changes in the definition"
      " of targets in the package 'ROL'.  Or, to maintain compatibility with"
      " older or newer versions the project 'Trilinos', instead link against the"
      " libraries specified by the variable 'ROL_LIBRARIES'."
      )
    string(REPLACE ";" "" deprecationMessage "${deprecationMessage}")
    set_target_properties(${libname}
      PROPERTIES DEPRECATION "${deprecationMessage}" )
  endif()
endforeach()
