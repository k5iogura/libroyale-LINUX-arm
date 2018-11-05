from __future__ import print_function
from __future__ import absolute_import

import os
import subprocess

import setuptools
from setuptools.command.build_py import build_py as _build_py

_LIB_NAME = 'royale_wrapper'


def _build_royale_wrapper(source_dir, build_dir):
    cmds = [
        ['cmake', '-B{}'.format(build_dir), '-H{}'.format(source_dir)],
        ['make', '-C', build_dir, 'VERBOSE=1'],
    ]

    for cmd in cmds:
        process = subprocess.Popen(cmd)
        process.wait()

        if process.returncode != 0:
            raise RuntimeError('Failed to execute: {}.'.format(cmd))


class _BuildPyCommand(_build_py):
    """Custom build command."""
    def run(self):
        source_dir = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(source_dir, _LIB_NAME)

        _build_royale_wrapper(source_dir, build_dir)
        _build_py.run(self)


def _setup():
    setuptools.setup(
        name=_LIB_NAME,
        version='v0.1.0',
        cmdclass={
            'build_py': _BuildPyCommand,
        },
        packages=setuptools.find_packages(),
        package_data={
            _LIB_NAME: [
                '_royale.so',
            ],
        },
        entry_points={
            'console_scripts': [
                'royale=royale_wrapper.main:main',
            ],
        }
    )


if __name__ == '__main__':
    _setup()
