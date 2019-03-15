# Find the Python package by running interpreter
# PYTHON_INCLUDE_PATH
# PYTHON_LIBRARIES
# PYTHON_FOUND
# will be set by this script

cmake_minimum_required(VERSION 2.6)

if(NOT PYTHON_EXECUTABLE)
  find_package(PythonInterp)
endif()

if (PYTHON_EXECUTABLE)
  # Find out the include path
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c
            "from __future__ import print_function;import os,sys;print(os.path.dirname(os.path.dirname(sys.executable)), end='')"
    OUTPUT_VARIABLE __python_path)
  # And the version
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c
            "from __future__ import print_function;import sys;print('{}.{}'.format(*sys.version_info[:2]), end='')"
    OUTPUT_VARIABLE __python_version)
else ()
  message(FATAL_ERROR "Python interpreter not found.")
endif ()

set (PYTHON_FOUND 1 CACHE INTERNAL "Python found")
set (PYTHON_INCLUDE_PATH "${__python_path}/include/python${__python_version}")
if (APPLE)
   set (PYTHON_LIBRARIES "${__python_path}/lib/libpython${__python_version}.dylib")
elseif (UNIX)
   set (PYTHON_LIBRARIES "${__python_path}/lib/libpython${__python_version}.so")
else ()
   message (FATAL_ERROR "Not implemented for this platform")
endif ()
