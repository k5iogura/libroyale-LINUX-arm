#!/bin/bash
cmake \
 -DCMAKE_CXX_COMPILER=g++ \
 -DCMAKE_C_COMPILER=gcc \
 -DCMAKE_INCLUDE_PATH=/home/pi/camboard/libroyale-3.20.0.62-LINUX-arm-32Bit/include/ \
 -DCMAKE_LIBRARY_PATH=/home/pi/camboard/libroyale-3.20.0.62-LINUX-arm-32Bit/bin/\
 -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations" \
 -DPYTHON_LIBRARIES=/usr/lib/arm-linux-gnueabihf/ \
 ..
