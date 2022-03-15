import os

from setuptools import Extension, setup

setup(ext_modules=[Extension('test_package.simple',
                             [os.path.join('test_package', 'simple.c')])])
