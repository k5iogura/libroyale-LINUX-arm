# PMD CamBoard on RaspberryPi-3 Model B+

### Requirement:  
- PMD CamBoard pico flexx
- RaspberryPi-3 Model B+
- Raspbian stretch
- CamBoard SDK

### Install and Check

***Add udev rule*** for CamBoard( id == 1c27 ) and add pi user to plugdev group.

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
