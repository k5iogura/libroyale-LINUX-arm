%module royale

%{
#define SWIG_FILE_WITH_INIT
#define ROYALE_NEW_API_2_2_0
#define ROYALE_FINAL_API_2_2_0
#define ROYALE_C_API_VERSION 220

#include <DepthDataCAPI.h>
#include <DepthImageCAPI.h>
#include <CameraDeviceCAPI.h>
#include <CameraManagerCAPI.h>
%}

%include CustomAPI.i
