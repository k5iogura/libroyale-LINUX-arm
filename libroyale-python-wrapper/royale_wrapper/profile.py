from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from royale_wrapper import royale


def profile():
    manager = royale.CameraManager()
    manager.initialize()
    cameras = manager.get_connected_cameras()

    print('Found {} cameras'.format(len(cameras)))
    for index, id_ in enumerate(cameras):
        handle = manager.create_camera_device(id_)
        camera = royale.CameraDevice(handle)
        camera.initialize()

        print('Camera:', index)
        print('  ID:', id_)
        print('  Name:', camera.get_camera_name())

        print('  Info:')
        for key, value in camera.get_camera_info().items():
            print('    {}: {}'.format(key, value))

        print('  Use Case:')
        for case in camera.get_use_cases():
            print('    - {}'.format(case))
        print()
