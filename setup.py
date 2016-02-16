#!/usr/bin/env python3

from setuptools import setup
from hipscud.version import __version__
import glob
import os

def _data_files():
    for theme in ['hicolor', 'ubuntu-mono-dark', 'ubuntu-mono-light', 'elementary']:
        directory = os.path.join('share', 'icons', theme, 'scalable', 'apps')
        files = glob.glob(os.path.join('share', 'icons', theme, '*.svg'))
        yield directory, files

    yield os.path.join('share', 'doc', 'hipscud'), \
        ['LICENSE', 'README']
    yield os.path.join('share', 'applications'), \
        glob.glob(os.path.join('share', '*.desktop'))
    yield os.path.join('share', 'pixmaps'), \
        glob.glob(os.path.join('hipscud', 'resources', 'hipscud.png'))


setup(name='hipscud',
      author='Charlie Wolf',
      author_email='charlie@flow180.com',
      data_files=list(_data_files()),
      description='HipScud is a non official desktop client for hipchat',
      entry_points = {
          'gui_scripts': ['hipscud = hipscud.__main__:main'],
      },
      keywords = "hipchat chat im instant_message",
      license = "MIT",
      maintainer='Andrew Stiegmann',
      maintainer_email='andrew.stiegmann@gmail.com',
      package_data={'hipscud': ['resources/*',]},
      packages=['hipscud',],
      requires=['dbus', 'PyQt4',],
      url='https://github.com/flow180/hipscud',
      version = __version__,
)
