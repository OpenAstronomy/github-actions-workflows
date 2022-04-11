import os

if os.getenv("GITHUB_WORKFLOW") == ".github/workflows/test_publish.yml":
    from . import simple

    __all__ = ["simple"]
