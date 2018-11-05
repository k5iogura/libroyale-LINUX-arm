from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import argparse

from . import profile
from . import test


def _parse_command_line_args():
    ap = argparse.ArgumentParser(
        description='Test royale API'
    )
    ap.add_argument('mode', choices=['profile', 'test'])
    return ap.parse_args(sys.argv[1:2])


def main():
    args = _parse_command_line_args()
    if args.mode == 'profile':
        profile.profile()
    else:
        test.test()
