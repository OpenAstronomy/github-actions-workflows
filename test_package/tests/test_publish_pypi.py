import os
import subprocess
import sys
from pathlib import Path


def test_build_package():
    """Test that the package can be built successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", "dist"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Build failed: {result.stderr}"

    # Check that distribution files were created
    dist_dir = Path("dist")
    assert dist_dir.exists(), "dist directory not created"

    dist_files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
    assert len(dist_files) > 0, "No distribution files created"


def test_publish_to_test_pypi():
    """Test publishing package to Test PyPI.

    This test requires TWINE_USERNAME and TWINE_PASSWORD environment variables
    to be set for Test PyPI authentication.

    To run this test:
    1. Set TWINE_USERNAME (usually '__token__')
    2. Set TWINE_PASSWORD (your Test PyPI API token)
    3. Run: pytest test_package/tests/test_publish_pypi.py::test_publish_to_test_pypi
    """
    # Skip if credentials are not available
    if not os.getenv("TWINE_USERNAME") or not os.getenv("TWINE_PASSWORD"):
        import pytest
        pytest.skip("TWINE_USERNAME and TWINE_PASSWORD not set")

    # First build the package
    build_result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", "dist"],
        capture_output=True,
        text=True
    )
    assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"

    # Upload to Test PyPI
    upload_result = subprocess.run(
        [
            sys.executable, "-m", "twine", "upload",
            "--repository", "testpypi",
            "--skip-existing",
            "dist/*"
        ],
        capture_output=True,
        text=True
    )

    # Check result (skip-existing means it's ok if already uploaded)
    assert upload_result.returncode == 0, f"Upload failed: {upload_result.stderr}"
    print(f"Upload output: {upload_result.stdout}")


def test_check_package_metadata():
    """Test that package metadata is valid for PyPI."""
    # Build first
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", "dist"],
        capture_output=True,
        text=True
    )

    # Check with twine
    result = subprocess.run(
        [sys.executable, "-m", "twine", "check", "dist/*"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Package check failed: {result.stderr}"
    assert "PASSED" in result.stdout, "Package metadata validation failed"
