import argparse
import cv2
import numpy as np

from primesense import openni2

args = argparse.ArgumentParser()
args.add_argument("-k", "--waitKey", type=int, default=0,  help="waitKey value")
args = args.parse_args()

openni2.initialize()     # can also accept the path of the OpenNI redistribution

dev = openni2.Device.open_any()
print(dev.get_sensor_info(openni2.SENSOR_DEPTH))

depth_stream = dev.create_depth_stream()
#depth_stream = dev.create_ir_stream()
depth_stream.start()
#print(depth_array.shape)
while True:
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    depth_array = np.ndarray((frame.height,frame.width),dtype=np.uint16,buffer=frame_data)
    da1d = depth_array.reshape(frame.height*frame.width)
    mx1d = max(da1d)
    depth_array = depth_array / mx1d
    cv2.imshow('depth_array', depth_array)
    if cv2.waitKey(args.waitKey) != -1: break

depth_stream.stop()
openni2.unload()

