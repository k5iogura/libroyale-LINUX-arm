#!/usr/bin/env python3
import argparse
from pdb import *
import sys,os
import cv2
import numpy as np
from time import time,sleep
import queue
import multiprocessing as mp

# For OpenVINO
from openvino.inference_engine import IENetwork, IEPlugin

# For PICO FLEXX
import roypy
# from demo_camera import MyListener, main
from sample_camera_info import print_camera_info
from roypy_sample_utils import CameraOpener, add_camera_opener_options
from roypy_platform_utils import PlatformHelper

LABELS = ('background',
          'aeroplane', 'bicycle', 'bird', 'boat',
          'bottle', 'bus', 'car', 'cat', 'chair',
          'cow', 'diningtable', 'dog', 'horse',
          'motorbike', 'person', 'pottedplant',
          'sheep', 'sofa', 'train', 'tvmonitor')

def overlay_on_image(args, display_image, object_info, depth_image):

    min_score_percent = 50  # detector threshold %

    source_image_width  = display_image.shape[1]
    source_image_height = display_image.shape[0]

    base_index = 0
    class_id   = object_info[base_index + 1]
    percentage = int(object_info[base_index + 2] * 100)
    if (percentage <= min_score_percent):
        # ignore boxes
        return display_image

    label_text = LABELS[int(class_id)] + " (" + str(percentage) + "%)"
    box_left   = max(int(object_info[base_index + 3] * source_image_width), 0)
    box_top    = min(int(object_info[base_index + 4] * source_image_height),depth_image.shape[0]-1)
    box_right  = max(int(object_info[base_index + 5] * source_image_width), 0)
    box_bottom = min(int(object_info[base_index + 6] * source_image_height),depth_image.shape[0]-1)

    # aply depth effect
    assert depth_image.shape==display_image.shape[:2],str(depth_image.shape)+str(display_image.shape)
    assert isinstance(depth_image[0][0],np.uint8)    ,str(type(depth_image[0][0]))
    object_region = np.zeros(display_image.shape[:2],dtype=np.uint8)                # HW
    object_region[box_top:box_bottom,box_left:box_right]=depth_image[box_top:box_bottom,box_left:box_right]
    if not args.usedepth: object_region[object_region>0] = 255
    display_image = make_effect(display_image, object_region, class_id)

    box_color     = (255, 128, 0)  # box color
    box_thickness = 1
    display_image = cv2.rectangle(
        display_image, (box_left, box_top), (box_right, box_bottom), box_color, box_thickness)

    label_background_color = (125, 175,  75)
    label_text_color       = (255, 255, 255)  # white text

    label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    label_left = box_left
    label_top  = box_top - label_size[1]
    if (label_top < 1):
        label_top = 1
    label_right   = label_left + label_size[0]
    label_bottom  = label_top + label_size[1]
    display_image = cv2.rectangle(display_image,
        (label_left - 1, label_top - 1), (label_right + 1, label_bottom + 1), label_background_color, -1)
    # label text above the box
    display_image = cv2.putText(display_image,
        label_text, (label_left, label_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_text_color, 1)
    return display_image

def make_effect(src, depth, class_id=0):
    assert len(src.shape)==3 and len(depth.shape)==2, str(src.shape)+str(depth.shape)
    assert isinstance(src,np.ndarray) and isinstance(depth,np.ndarray)
    depth0 = np.full(depth.shape,0,dtype=np.uint8)
    effect= np.zeros((3, depth.shape[0], depth.shape[1]),dtype=np.uint8) # CHW
    if class_id==18:     #sofa
        effect[0]=depth0
        effect[1]=depth
        effect[2]=depth0
    elif class_id%3==0:  #bird bus chair dog person sofa
        effect[0]=depth0
        effect[1]=depth0
        effect[2]=depth
    elif class_id%4==0:  #boat cat pottedplant tvmonitor
        effect[0]=depth0
        effect[1]=depth
        effect[2]=depth0
    elif class_id%7==0:  #car motorbike
        effect[0]=depth0
        effect[1]=depth
        effect[2]=depth0
    elif class_id%2==0:  #bicycle cow
        effect[0]=depth0
        effect[1]=depth0
        effect[2]=depth0
    else:                #aeroplane bottle diningtable horse sheep train
        effect[0]=depth
        effect[1]=depth
        effect[2]=depth
    effect = effect.transpose((1,2,0))  # HWC
    src[np.where(effect>0)] = 0
    src += effect
    return src

def process_event_queue (g,args,z=None):
    model_xml='vinosyp/models/SSD_Mobilenet/FP32/MobileNetSSD_deploy.xml'
    model_bin='vinosyp/models/SSD_Mobilenet/FP32/MobileNetSSD_deploy.bin'
    model_xml = os.environ['HOME'] + "/" + model_xml
    model_bin = os.environ['HOME'] + "/" + model_bin
    net = IENetwork(model=model_xml, weights=model_bin)	#R5

    plugin = IEPlugin(device=args.device, plugin_dirs=None)
    if args.device=='CPU':
        HOME=os.environ['HOME']
        LIBCPU_EXTENSION = HOME+"/inference_engine_samples/intel64/Release/lib/libcpu_extension.so"
        if not os.path.exists(LIBCPU_EXTENSION):
            print('run sample such as demo_squeezenet_download_convert_run.sh')
            sys.exit(-1)
        PATHLIBEXTENSION = os.getenv(
            "PATHLIBEXTENSION",
            LIBCPU_EXTENSION
        )
        plugin.add_cpu_extension(PATHLIBEXTENSION)
    exec_net = plugin.load(network=net, num_requests=1)

    input_blob = next(iter(net.inputs))  #input_blob = 'data'
    out_blob   = next(iter(net.outputs)) #out_blob   = 'detection_out'
    model_n, model_c, model_h, model_w = net.inputs[input_blob].shape #Tool kit R4
    print("n/c/h/w (from xml)= %d %d %d %d"%(model_n, model_c, model_h, model_w))
    print("input_blob : out_blob =",input_blob,":",out_blob)

    del net

    start = time()
    done_frame=0
    while True:
        try:# Depth Image
            itemZ= z.get(True, 5) # HW float
        except queue.Empty:
            print("\nDepth image queue timeout and continue program")
        else:
            pass
            #print(" ",len(itemZ[itemZ>0.]), np.max(itemZ), np.min(itemZ[itemZ!=0]))

        try:# Gray Image
            item = g.get(True, 5) # orignal version
        except queue.Empty:
            print("\nGray image queue timeout and exit from program")
            break
        else:
            frame_org = np.zeros((3, item.shape[0], item.shape[1]),dtype=np.uint8)  # CHW uint8
            flexx_image = item*255.
            flexx_image = flexx_image.astype(np.uint8)
            frame_org[0] = frame_org[1] = frame_org[2] = flexx_image
            frame_org = frame_org.transpose((1,2,0))                                # CHW => HWC uint8
            if frame_org is None:break
            frame = cv2.resize(frame_org,(model_w, model_h)).astype(dtype=np.float) # HWC uint8 => float
            frame-= 127.5       # means
            frame*= 0.007853    # scale

            in_frame = frame.transpose((2, 0, 1))                                   # HWC => CHW  float
            in_frame = in_frame.reshape((model_n, model_c, model_h, model_w))       # CHW => NCHW float

            exec_net.start_async(request_id=0, inputs={input_blob: in_frame})

            if exec_net.requests[0].wait(-1) == 0:
                res = exec_net.requests[0].outputs[out_blob]
                itemZ = (255*itemZ).astype(np.uint8)
                for j in range(res.shape[2]):
                    if res[0][0][j][0] < 0:break
                    frame_ov = overlay_on_image(args,frame_org.copy(),res[0][0][j],itemZ) # HWC uint8 => uint8
                if not isinstance(frame_ov,type(None)):
                    cv2.imshow('USB-Camera',frame_ov)
                key=cv2.waitKey(1)
                if key != -1:break
            else:
                print("error")
            # FPS
            done_frame+=1
            end = time()+1e-10
            sys.stdout.write('\b'*20)
            sys.stdout.write("%10.2f FPS"%(done_frame/(end-start)))
            sys.stdout.flush()
    #       painter.paint (item) # original code
    print("\nfinished")
    cv2.destroyAllWindows()
    del exec_net
    del plugin

class MyListener(roypy.IDepthDataListener):
    def __init__(self, g, mode, z=None):
        super(MyListener, self).__init__()
        self.queue = g
        self.queueZ= z
        self.mode  = mode
        if mode == 1:print("View Gray Mode")
        if mode == 2:print("View Confidence Mode")
        if mode == 3:print("View Gray * Confidence Mode")
        if mode == 4:print("View Gray * Confidence * Depth Mode")
        if mode == 0:print("View Depth Mode")

    def onNewData(self, data):
        values = []
        count = 0
        valueZ= np.zeros(data.height*data.width,dtype=np.float32)
        for i in range(data.getNumPoints()):
            if self.mode == 1:     # Gray
                values.append(data.getGrayValue(i)/255.)
                if count%10 == 0:
                    valueZ[count] = data.getZ(i)
                count+=1

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

        valueG = np.asarray(values)
        p = valueG.reshape(-1, data.width)        
        if self.queue.full():
            self.queue.get()
        self.queue.put(p)

        p = valueZ.reshape(-1, data.width)
        if self.queueZ.full():
            self.queueZ.get()
        self.queueZ.put(p)

def flexx (args):
    opener = CameraOpener(args)
    cam = opener.open_camera()

    print_camera_info(cam)
    cam.setUseCase(args.name)
    print("isConnected", cam.isConnected())
    print("getFrameRate", cam.getFrameRate())

    #g = queue.Queue(args.queues)   # Gray  image Queue
    #z = queue.Queue(args.queues)   # Depth image Queue
    g = mp.Queue(args.queues)   # Gray  image Queue
    z = mp.Queue(args.queues)   # Depth image Queue
    l = MyListener(g,args.mode,z)  # Listener
    cam.registerDataListener(l)    # Regist Listener
    cam.startCapture()             # start flexx
    process_event_queue(g,args,z)  # camera loop with Inference
    cam.stopCapture()              # stop  flexx

def main():
    args = argparse.ArgumentParser()
    add_camera_opener_options(args)
    args.add_argument("-d","--device", type=str, default='MYRIAD',help='on Device')
    args.add_argument("-m", "--mode",  type=int, default=1, help="ModeNo.")
    args.add_argument("-n", "--name",  type=str, default='MODE_5_45FPS_500', help="ModeName.")
    args.add_argument("-q", "--queues",type=int, default=33*5, help="Depth of Queue.")
    args.add_argument("-ud","--usedepth",action='store_true', help="full highlight for objects")
    args = args.parse_args()

    flexx(args)

if __name__=='__main__':
    main()

