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
