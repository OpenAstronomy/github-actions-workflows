from setuptools import Extension, find_packages, setup

setup(
    packages=find_packages(),
    ext_modules=[
        Extension("subpackage_c._example", ["subpackage_c/_example.c"]),
    ],
)
