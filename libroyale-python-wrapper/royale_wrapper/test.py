from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import time
import argparse
from royale_wrapper import royale

import numpy as np
import scipy.misc


def _normalize_image(image, max_val=None):
    max_val = max_val or np.max(image)
    return (image / max_val * 255).astype(np.uint8)


def _save_image(gray_image, x_image, y_image, z_image):
    _save_image.counter += 1

    if not _save_image.enabled:
        return

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    print('Saving image:', _save_image.counter)
    filename = 'tmp/{:03d}_x.png'.format(_save_image.counter)
    scipy.misc.imsave(filename, _normalize_image(x_image, 3))
    filename = 'tmp/{:03d}_y.png'.format(_save_image.counter)
    scipy.misc.imsave(filename, _normalize_image(y_image, 3))
    filename = 'tmp/{:03d}_z.png'.format(_save_image.counter)
    scipy.misc.imsave(filename, _normalize_image(z_image, 3))
    filename = 'tmp/{:03d}_gray.png'.format(_save_image.counter)
    scipy.misc.imsave(filename, gray_image)


_save_image.counter = 0
_save_image.enabled = True


def _parse_command_line_args():
    ap = argparse.ArgumentParser(
        description='Test royale API'
    )
    ap.add_argument('camera')
    ap.add_argument('--use_case')
    ap.add_argument('--disable-save', action='store_true')
    return ap.parse_args(sys.argv[2:])


def _get_camera(id_):
    manager = royale.CameraManager()
    manager.initialize()
    manager.get_connected_cameras()
    h_camera = manager.create_camera_device(id_)
    del manager
    return royale.CameraDevice(h_camera)


def test():
    """Test royale_wrapper"""
    args = _parse_command_line_args()

    camera = _get_camera(args.camera)
    camera.initialize()

    print('Name:', camera.get_camera_name())

    if args.use_case:
        camera.set_use_case(args.use_case)

    print('Using:', camera.get_current_use_case())
    _save_image.enabled = not args.disable_save

    camera.register_python_callback(_save_image)
    camera.register_data_listener()

    print('Capturing for 5 sec')
    camera.start_capture()
    time.sleep(5)
    counter = _save_image.counter
    print('Stop capturing')
    camera.stop_capture()
    print('Callback called {} times. ({} /sec)'.format(counter, counter / 5))

    time.sleep(1)
    camera.unregister_data_listener()
    camera.unregister_python_callback()
