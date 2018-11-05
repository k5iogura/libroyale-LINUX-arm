# Find include files
find_path(_ROYALE_INCLUDE_DIR royaleCAPI/royaleCAPI.h)
set(ROYALE_INCLUDE_DIR "${_ROYALE_INCLUDE_DIR}/royaleCAPI")

# Find libraries
if (APPLE)
   set(_ROYALE_C_LIB "libroyaleCAPI.dylib")
elseif (UNIX)
   set(_ROYALE_C_LIB "libroyaleCAPI.so")
else ()
   message(FATAL_ERROR "Not implemented for this platform")
endif()
find_library(ROYALE_LIB NAMES ${_ROYALE_C_LIB})

# Check
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(
    LibRoyale DEFAULT_MSG ROYALE_INCLUDE_DIR ROYALE_LIB
)

# Flag configuration copied from official royale-config.cmake
if (WIN32)
   SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D_WINDOWS /W3 /GR /EHsc /fp:fast /arch:SSE2 /Oy /Ot /D_VARIADIC_MAX=10 /DNOMINMAX /MD" CACHE STRING "" FORCE)
   SET(CMAKE_CXX_FLAGS_DEBUG "/Zi /Ob0 /Od /MD /RTC1" CACHE STRING "" FORCE)
   SET(CMAKE_CXX_FLAGS_MINSIZEREL "/O1 /Ob1 /D NDEBUG /MD" CACHE STRING "" FORCE)
   SET(CMAKE_CXX_FLAGS_RELWITHDEBINFO "/Zi /O2 /Ob1 /D NDEBUG /MD" CACHE STRING "" FORCE)
elseif (APPLE)
   SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wall -Wsign-compare -Wuninitialized -Wunused -Wno-deprecated-declarations -std=c++11" CACHE STRING "" FORCE)
elseif (UNIX)
   SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -std=c++0x -Wall -Wconversion" CACHE STRING "" FORCE)
else ()
   message(FATAL_ERROR "Not implemented for this platform")
endif ()
