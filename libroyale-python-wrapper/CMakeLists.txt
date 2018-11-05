cmake_minimum_required(VERSION 2.8)

### Check Python, NumPy and libroyale
set (CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package (Python REQUIRED)
find_package (NumPy REQUIRED)
find_package (Royale REQUIRED)

### Check SWIG
find_package (SWIG REQUIRED)
include (${SWIG_USE_FILE})
include (GenerateExportHeader)

### Setup wrapper
include_directories (
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${PROJECT_BINARY_DIR}
    ${ROYALE_INCLUDE_DIR}
    ${PYTHON_INCLUDE_PATH}
    ${PYTHON_NUMPY_INCLUDE_DIR}
)

# set (CMAKE_SWIG_FLAGS "-Wall")

set (INTERFACE_FILE src/royale.i)

set (CMAKE_VERBOSE_MAKEFILE on)

set_source_files_properties(${INTERFACE_FILE} PROPERTIES CPLUSPLUS ON)
swig_add_module(royale python ${INTERFACE_FILE})
swig_link_libraries(royale ${PYTHON_LIBRARIES} ${ROYALE_LIB})
