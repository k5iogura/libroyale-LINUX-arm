#!/usr/bin/python3

# Copyright (C) 2017 Infineon Technologies & pmdtechnologies ag
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

"""This sample shows how to shows how to capture image data.

It uses Python's numpy and matplotlib to process and display the data.
"""

import argparse
import roypy
import time
import queue
from sample_camera_info import print_camera_info
from roypy_sample_utils import CameraOpener, add_camera_opener_options
from roypy_platform_utils import PlatformHelper

import numpy as np
import cv2

class MyListener(roypy.IDepthDataListener):
    def __init__(self, q, mode):
        super(MyListener, self).__init__()
        self.queue = q
        self.mode  = mode
        if mode == 1:print("View Gray Mode")
        if mode == 2:print("View Confidence Mode")
        if mode == 3:print("View Gray * Confidence Mode")
        if mode == 4:print("View Gray * Confidence * Depth Mode")
        if mode == 0:print("View Depth Mode")

    def onNewData(self, data):
        values = []
        for i in range(data.getNumPoints()):
            if self.mode == 1:     # Gray
                values.append(data.getGrayValue(i)/255.)

            elif self.mode == 2:   # Confidence
                values.append(data.getDepthConfidence(i)/255.)

            elif self.mode == 3:   # Gray * Confidence
                c = data.getDepthConfidence(i)/255.
                g = data.getGrayValue(i)/255.
                values.append(c*g)

            elif self.mode == 4:   # Gray * Confidence * Z
                z = data.getZ(i)
                c = data.getDepthConfidence(i)/255.
                g = data.getGrayValue(i)/255.
                values.append(c*g*z)
            else:                  # Z
                values.append(data.getZ(i))

        array = np.asarray(values)
        p = array.reshape (-1, data.width)        
        if self.queue.full():
            self.queue.get()
        self.queue.put(p)

    def paint (self, data):
        """Called in the main thread, with data containing one of the items that was added to the
        queue in onNewData.
        """
        # create a figure and show the raw data
        cv2.imshow('Demo',cv2.resize(data,(640,480)))

def main ():
    platformhelper = PlatformHelper()
    parser = argparse.ArgumentParser (usage = __doc__)
    add_camera_opener_options (parser)
    parser.add_argument ("--seconds", type=int, default=15, help="duration to capture data")
    parser.add_argument ("-m", "--mode", type=int, default=0, help="ModeNo.")
    parser.add_argument ("-n", "--name", type=str, default='MODE_5_45FPS_500', help="ModeName.")
    parser.add_argument ("-q", "--queues", type=int, default=3, help="Depth of Queue.")
    options = parser.parse_args()
    opener = CameraOpener (options)
    cam = opener.open_camera ()

    print_camera_info (cam)
    print("isConnected", cam.isConnected())
    print("getFrameRate", cam.getFrameRate())

    # we will use this queue to synchronize the callback with the main
    # thread, as drawing should happen in the main thread
    q = queue.Queue(options.queues)
    l = MyListener(q,options.mode)
    cam.registerDataListener(l)
    cam.setUseCase(options.name)
    cam.startCapture()
    # create a loop that will run for a time (default 15 seconds)
    process_event_queue (q, l, options.seconds)
    cam.stopCapture()

def process_event_queue (q, painter, seconds):
    # create a loop that will run for the given amount of time
    t_end = time.time() + seconds
    while True:
        try:
            # try to retrieve an item from the queue.
            # this will block until an item can be retrieved
            # or the timeout of 1 second is hit
            item = q.get(True, 1)
        except queue.Empty:
            # this will be thrown when the timeout is hit
            break
        else:
            painter.paint (item)
        if cv2.waitKey(1)!=-1:break

if (__name__ == "__main__"):
    main()
