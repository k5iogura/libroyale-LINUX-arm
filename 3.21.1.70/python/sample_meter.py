#!/usr/bin/python3
import sys,os

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
# import matplotlib.pyplot as plt

class MyListener(roypy.IDepthDataListener):
    def __init__(self, q,xq,yq):
        super(MyListener, self).__init__()
        self.queue = q
        self.xq = xq
        self.yq = yq

    def onNewData(self, data):
        zvalues = []
        xvalues = []
        yvalues = []
        for i in range(data.getNumPoints()):
            zvalues.append(data.getZ(i))
            xvalues.append(data.getX(i))
            yvalues.append(data.getY(i))

        zarray = np.asarray(zvalues)
        p = zarray.reshape (-1, data.width)        
        self.queue.put(p)

        xarray = np.asarray(xvalues)
        p = xarray.reshape (-1, data.width)        
        self.xq.put(p)

        yarray = np.asarray(yvalues)
        p = yarray.reshape (-1, data.width)        
        self.yq.put(p)

    def paint (self, data):
        """Called in the main thread, with data containing one of the items that was added to the
        queue in onNewData.
        """
        # create a figure and show the raw data
        plt.figure(1)
        plt.imshow(data)

        plt.show(block = False)
        plt.draw()
        # this pause is needed to ensure the drawing for
        # some backends
        plt.pause(0.001)

def main ():
    platformhelper = PlatformHelper()
    parser = argparse.ArgumentParser (usage = __doc__)
    add_camera_opener_options (parser)
    parser.add_argument ("--seconds", type=int, default=15, help="duration to capture data")
    options = parser.parse_args()
    opener = CameraOpener (options)
    cam = opener.open_camera ()

    print_camera_info (cam)
    print("isConnected", cam.isConnected())
    print("getFrameRate", cam.getFrameRate())

    # we will use this queue to synchronize the callback with the main
    # thread, as drawing should happen in the main thread
    q = queue.Queue()
    xq= queue.Queue()
    yq= queue.Queue()
    l = MyListener(q,xq,yq)
    cam.registerDataListener(l)
    cam.startCapture()
    # create a loop that will run for a time (default 15 seconds)
    process_event_queue(q,xq,yq, l, options.seconds)
    cam.stopCapture()

def process_event_queue(q, xq, yq, painter, seconds):
    # create a loop that will run for the given amount of time
    t_end = time.time() + seconds
    while time.time() < t_end:
        try:
            # try to retrieve an item from the queue.
            # this will block until an item can be retrieved
            # or the timeout of 1 second is hit
            item = q.get(True, 1)
            itemx= xq.get(True, 1)
            itemy= yq.get(True, 1)
        except queue.Empty:
            # this will be thrown when the timeout is hit
            break
        else:
            #painter.paint (item)
            h,w = int(item.shape[0]/2)+1, int(item.shape[1]/2)+1
            meter = item[h][w]
            meter = int(100.*meter)/100.
            xmax,xmin = np.max(itemx), np.min(itemx)
            ymax,ymin = np.max(itemy), np.min(itemy)
            if meter == 0.0:
                distance="distance < 0.45m %d %d"%(h,w)
            else:
                distance="%.2fm %.4f %.4f %.4f %.4f"%(meter,xmin,ymin,xmax,ymax)
            sys.stdout.write('\b'*50)
            sys.stdout.write(distance)
            sys.stdout.flush()
    print("\nfinalizing")

if (__name__ == "__main__"):
    main()
