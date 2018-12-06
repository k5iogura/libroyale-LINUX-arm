# PMD CamBoard on RaspberryPi-3 Model B+

## [royale + openni2 feasibility study](royale+openni2.md)

### Requirement:  
- PMD CamBoard pico flexx
- RaspberryPi-3 Model B+
- Raspbian stretch
- CamBoard SDK 3.20.0.62(Sh!CBpf)

### Install and Check

***Add udev rule*** for CamBoard( id == 1c27 ) and add "pi" user to plugdev group to make use usb device available without Super Users previlege.

```
# cp driver/udev/10-royale-ubuntu.rules /etc/udev/rules.d/
$ id
...,46(plugdev), ...
```

***Insert CamBoard*** via USB port( 2.0 ).  
Status after inserting CamBoard via USB port is bellow,

```
$ lsusb
Bus 001 Device 005: ID 1c27:c012

$ dmesg
...
usb 1-1.3: new high-speed USB device number 5 using dwc_otg
usb 1-1.3: New USB device found, idVendor=1c28, idProduct=c012
usb 1-1.3: New USB device strings: Mfr=1, Product=2, SerialNumber=0
usb 1-1.3: Product: FX3
usb 1-1.3: Manufactureer: PMDtec
```

***Run sampleCameraInfo,***

```
$ export LD_LIBRARY_PATH=`pwd`/bin
$ bin/sampleCameraInfo
Detected 1 camera(s).
======================
  Camera Information
======================
Id:         0007-2103-0181-1303
Type:       PICOFLEXX
Width:      224
Height:     171
Operation modes: 7
   MODE_9_5FPS_2000
   ...
     this operation mode has 2 streams
CameraInfo items: 7
  ( BRIDGE_TYPE, Enclustra )
  ...
```
Check is over.  

### C++ samples

[Document of ./samples/ directory is here](samples/README_samples.md)

### OpenNI2 + sampleOpenNI2Driver

To use flexx with Python, install bellow,  
- [OpenNI2 library](https://structure.io/openni)
- [primesense module](https://pypi.org/project/primesense/)
- [libroyaleONI2.so, libroyale.so, libspectre3.so](samples/cpp/sampleOpenNI2Drivers/README-OpenNI2-Drivers.md)

Install openni library and primesense module.
```
# apt install libopenni2-0 libopenni2-dev
//check
$ ls /etc/openni2
OpenNI.ini

$ pip3 install primesense
//check
python3 -c "import primesense
$
```

Make driver *.so and locate them in default library directory.
```
// install in default place such as /usr/lib/OpenNI2/Drivers/
// sample/bin/libroyale.so sample/bin/libspectre3.so
# cp sample/bin/libroyale.so.3.20.0 sample/bin/libspectre3.so /usr/lib/OpenNI2/Drivers

// Need to make libroyalONI2.so*
$ cd sampes/cpp/sampleOpenNI2Driver
$ cmake .
$ make
//check
$ ls *.so*
libroyaleONI2.so -> libroyaleONI2.so.0
// install in default place such as /usr/lib/OpenNI2/Drivers/
# cp libroyaleONI2.so.0 /usr/lib/OpenNI2/Drivers

// make so name
# cd /usr/lib/OpenNI2/Drivers
# ln -s libroyale.so.3.20.0 libroyale.so
# ln -s libroyaleONI2.so.0  libroyaleONI2.so

// patching(I don't know why)
# ln /usr/lib/libOpenNI2.so.0 .
# ln -s libOpenNI2.so.0 libOpenNI2.so

// after all,,,
# ls *.so
libDummyDevice.so libOniFile.so libOpenNI2.so libPS1080.so libPSLink.so libroyaleONI2.so libroyale.so
```

To check environment easy,

```
$ export OPENNI2_REDIST=/usr/lib/OpenNI2/Drivers
$ python3 -c "from primesense import openni2;openni2.initialize();openni2.unload()"
```
If silence it's good!

To check environment by python script,
```
$ cat websample.py

import cv2
import numpy as np

from primesense import openni2
openni2.initialize()     # can also accept the path of the OpenNI redistribution

dev = openni2.Device.open_any()
print(dev.get_sensor_info(openni2.SENSOR_DEPTH))

depth_stream = dev.create_depth_stream()
depth_stream.start()
frame = depth_stream.read_frame()
frame_data = frame.get_buffer_as_uint16()
depth_stream.stop()

depth_array = np.ndarray((frame.height,frame.width),dtype=np.uint16,buffer=frame_data)
da1d = depth_array.reshape(frame.height*frame.width)
mx1d = max(da1d)
depth_array = depth_array / mx1d
print(depth_array.shape)
cv2.imshow('depth_array', depth_array)
while True:
    if cv2.waitKey(1) != -1: break

openni2.unload()

$ python3 websample.py
```
My right hand seen!  

![](files/OpenNI2_first.png)

This is the end of OpenNI2 + OpenNI2Driver Feasiblity Study:-)
