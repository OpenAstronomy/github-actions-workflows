import os

if os.getenv("GITHUB_WORKFLOW") == ".github/workflows/test_publish.yml":
    from setuptools import Extension, setup

    setup(ext_modules=[Extension('test_package.simple',
                                 [os.path.join('test_package', 'simple.c')])])
else:
    from setuptools import setup

    setup()
