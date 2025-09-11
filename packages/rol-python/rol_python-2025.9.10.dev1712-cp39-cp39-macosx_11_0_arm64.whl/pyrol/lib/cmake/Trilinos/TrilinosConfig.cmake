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
# CMake variable for use by Trilinos clients. 
#
# Do not edit: This file was generated automatically by CMake.
#
##############################################################################

if(CMAKE_VERSION VERSION_LESS 3.3)
  set(${CMAKE_FIND_PACKAGE_NAME}_NOT_FOUND_MESSAGE
    "Trilinos requires CMake 3.3 or later for 'if (... IN_LIST ...)'"
    )
  set(${CMAKE_FIND_PACKAGE_NAME}_FOUND FALSE)
  return()
endif()
cmake_minimum_required(VERSION 3.3...3.23.0)

## ---------------------------------------------------------------------------
## Compilers used by Trilinos build
## ---------------------------------------------------------------------------

set(Trilinos_CXX_COMPILER "/Applications/Xcode_16.4.app/Contents/Developer/usr/bin/g++")

set(Trilinos_C_COMPILER "/Applications/Xcode_16.4.app/Contents/Developer/usr/bin/gcc")

set(Trilinos_Fortran_COMPILER "")

## ---------------------------------------------------------------------------
## Compiler flags used by Trilinos build
## ---------------------------------------------------------------------------

set(Trilinos_CMAKE_BUILD_TYPE "RELEASE")

set(Trilinos_CXX_COMPILER_FLAGS [[ -O3 -DNDEBUG]])

set(Trilinos_C_COMPILER_FLAGS [[ -O3 -DNDEBUG]])

set(Trilinos_Fortran_COMPILER_FLAGS [[ ]])

## Extra link flags (e.g., specification of fortran libraries)
set(Trilinos_EXTRA_LD_FLAGS [[]])

## This is the command-line entry used for setting rpaths. In a build
## with static libraries it will be empty. 
set(Trilinos_SHARED_LIB_RPATH_COMMAND "-Wl,-rpath,/var/folders/x7/ch5v91h56_zbvbd1y2f600dm0000gn/T/tmpbmv8ykd1/wheel/platlib/pyrol/lib")
set(Trilinos_BUILD_SHARED_LIBS "ON")

set(Trilinos_LINKER /Applications/Xcode_16.4.app/Contents/Developer/usr/bin/ld)
set(Trilinos_AR /usr/bin/ar)


## ---------------------------------------------------------------------------
## Set library specifications and paths 
## ---------------------------------------------------------------------------

## The project version number
set(Trilinos_VERSION "16.2.0")

# For best practices in handling of components, see
# <http://www.cmake.org/cmake/help/v3.2/manual/cmake-developer.7.html#find-modules>.
#
# If components were requested, include only those. If not, include all of
# Trilinos.
if (Trilinos_FIND_COMPONENTS)
  set(COMPONENTS_LIST ${Trilinos_FIND_COMPONENTS})
else()
  set(COMPONENTS_LIST ROL;Teuchos;TeuchosRemainder;TeuchosNumerics;TeuchosComm;TeuchosParameterList;TeuchosParser;TeuchosCore)
endif()

# Initialize Trilinos_FOUND with true, and set it to FALSE if any of
# the required components wasn't found.
set(Trilinos_FOUND TRUE)
set(Trilinos_NOT_FOUND_MESSAGE "")
set(selectedComponentsFound "")
foreach (comp IN ITEMS ${COMPONENTS_LIST})
  set(compPkgConfigFile
    ${CMAKE_CURRENT_LIST_DIR}/../${comp}/${comp}Config.cmake
    )
  if (EXISTS ${compPkgConfigFile})
    # Set Trilinos_<component>_FOUND.
    set(Trilinos_${comp}_FOUND TRUE)
    # Include the package file.
    include(${compPkgConfigFile})
    # Add variables to lists.
    list(APPEND Trilinos_LIBRARIES ${${comp}_LIBRARIES})
    list(APPEND selectedComponentsFound ${comp})
  else()
    set(Trilinos_${comp}_FOUND FALSE)
    if(Trilinos_FIND_REQUIRED_${comp})
      string(APPEND Trilinos_NOT_FOUND_MESSAGE
        "ERROR: Could not find component '${comp}'!\n")
      set(Trilinos_FOUND FALSE)
    endif()
  endif()
endforeach()

# Deprecated (see #299)!
set(Trilinos_INCLUDE_DIRS "/var/folders/x7/ch5v91h56_zbvbd1y2f600dm0000gn/T/tmpbmv8ykd1/wheel/platlib/pyrol/include")

# Remove duplicates in Trilinos_LIBRARIES
list(REMOVE_DUPLICATES Trilinos_LIBRARIES)

## ---------------------------------------------------------------------------
## MPI specific variables
##   These variables are provided to make it easier to get the mpi libraries
##   and includes on systems that do not use the mpi wrappers for compiling
## ---------------------------------------------------------------------------

set(Trilinos_INSTALL_DIR "/var/folders/x7/ch5v91h56_zbvbd1y2f600dm0000gn/T/tmpbmv8ykd1/wheel/platlib/pyrol")
set(Trilinos_MPI_LIBRARIES "")
set(Trilinos_MPI_LIBRARY_DIRS "")
set(Trilinos_MPI_INCLUDE_DIRS "")
set(Trilinos_MPI_EXEC "")
set(Trilinos_MPI_EXEC_PRE_NUMPROCS_FLAGS "")
set(Trilinos_MPI_EXEC_MAX_NUMPROCS "")
set(Trilinos_MPI_EXEC_POST_NUMPROCS_FLAGS "")
set(Trilinos_MPI_EXEC_NUMPROCS_FLAG "")

## ---------------------------------------------------------------------------
## Compiler vendor identifications
## ---------------------------------------------------------------------------
set(Trilinos_SYSTEM_NAME "Darwin")
set(Trilinos_CXX_COMPILER_ID "AppleClang")
set(Trilinos_C_COMPILER_ID "AppleClang")
set(Trilinos_Fortran_COMPILER_ID "")
set(Trilinos_Fortran_IMPLICIT_LINK_LIBRARIES "")

## ---------------------------------------------------------------------------
## Set useful general variables 
## ---------------------------------------------------------------------------

## The packages enabled for this project
set(Trilinos_PACKAGE_LIST "ROL;Teuchos;TeuchosRemainder;TeuchosNumerics;TeuchosComm;TeuchosParameterList;TeuchosParser;TeuchosCore")

## The selected packages for this project
set(Trilinos_SELECTED_PACKAGE_LIST "${selectedComponentsFound}")

## ---------------------------------------------------------------------------
## Modern CMake (IMPORTED) targets
## ---------------------------------------------------------------------------

# Trilinos::all_libs  (Does *not* depend on COMPONENTS)
if (NOT TARGET Trilinos::all_libs)
  set(Trilinos_ALL_PACKAGES_TARGETS)
  foreach (pkg IN ITEMS ROL;Teuchos;TeuchosRemainder;TeuchosNumerics;TeuchosComm;TeuchosParameterList;TeuchosParser;TeuchosCore)
    list(APPEND Trilinos_ALL_PACKAGES_TARGETS ${pkg}::all_libs)
  endforeach()
  add_library(Trilinos::all_libs IMPORTED INTERFACE GLOBAL)
  target_link_libraries(Trilinos::all_libs
  INTERFACE ${Trilinos_ALL_PACKAGES_TARGETS} )
endif()

# Trilinos::all_selected_libs  (Depend on COMPONENTS)
if (NOT TARGET Trilinos::all_selected_libs)
  set(Trilinos_ALL_SELECTED_PACKAGES_TARGETS)
  foreach (pkg IN ITEMS ${selectedComponentsFound})
    list(APPEND Trilinos_ALL_SELECTED_PACKAGES_TARGETS ${pkg}::all_libs)
  endforeach()
  add_library(Trilinos::all_selected_libs IMPORTED INTERFACE GLOBAL)
  target_link_libraries(Trilinos::all_selected_libs
    INTERFACE ${Trilinos_ALL_SELECTED_PACKAGES_TARGETS} )
endif()
