import argparse
import cv2
import numpy as np
from pdb import *

from primesense import openni2

args = argparse.ArgumentParser()
args.add_argument("-k", "--waitKey", type=int, default=0,  help="waitKey value")
args = args.parse_args()

openni2.initialize()     # can also accept the path of the OpenNI redistribution

dev = openni2.Device.open_any()
print(dev.get_sensor_info(openni2.SENSOR_DEPTH))

depth_stream = dev.create_depth_stream()
#depth_stream = dev.create_ir_stream() # flexx not support
depth_stream.start()

dmax=mean=0
while True:
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    depth_array = np.ndarray((frame.height,frame.width),dtype=np.uint16,buffer=frame_data)
    mean = np.mean(depth_array)
    depth_array = depth_array / (2*mean)
    depth_array[depth_array>1.0] = 1.0
    depth_array *= 255
    depth_array = depth_array.astype(np.uint8)
    depth_array = cv2.applyColorMap(depth_array, cv2.COLORMAP_PINK)
    cv2.imshow('depth_array', depth_array)
    if cv2.waitKey(args.waitKey) != -1: break
print("data max ",dmax)
print("data mean",mean)

depth_stream.stop()
openni2.unload()

