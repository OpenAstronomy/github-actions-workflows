# github-actions-workflows

Reusable workflows for GitHub Actions.

## Build and publish a Python package

Build, test and publish a Python source distribution and collection of platform-dependent wheels.

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish.yml@main
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
      targets: |
        - linux
        - cp3?-macosx_x86_64
    secrets:
      pypi_password: ${{ secrets.pypi_password }}
```

### Inputs

#### targets
List of build targets for cibuildwheel. 
The list of targets must be specified as demonstrated by the default value below.
Each target is built within a separate matrix job.

If the target is `linux`, `macos` or `windows`, cibuildwheel is run on the latest version of that OS.

Any other target is assumed to be a value for the `CIBW_BUILD` environment variable (e.g. `cp3?-macosx_x86_64`).
In this case the OS to run cibuildwheel on is extracted from the target.

Targets that end with ``aarch64``, ``arm64`` and ``universal2`` are also supported without any additional configuration of cibuildwheel. 

***Note:** `targets` is a **string** and must be specified as a literal block scalar using the `|`. (Without the `|`, it must also be valid YAML.)*

Default is:
```yaml
targets: |
  - linux
  - macos
  - windows
```

To not build any wheels: 
```yaml
targets: ''
```

#### sdist
Whether to build a source distribution.
Default is `true`.

#### test_extras
Any `extras_requires` modifier that should be used to install the package for testing.
Default is none.

#### test_command
The command to run to test the package.
Will be run in a temporary directory.
Default is no testing.

#### libraries
Packages needed to build the source distribution for testing. Must be a string of space-separated apt packages.
Default is install nothing extra.

#### upload_to_pypi
Whether to always upload to PyPI after successful builds.
If `false`, successful builds are only uploaded when tags are pushed.
Default is `false`.

#### repository_url
The PyPI repository URL to use.
Default is the main PyPI repository.

#### submodules
Whether to checkout submodules.
Default is `true`.

### Secrets

#### pypi_password
The authentication token to access the PyPI repository.

## Build and publish a pure Python package

This the workflow is similar to the `publish.yml` workflow, except, instead of building wheels using cibuildwheel, a pure Python wheel and a source distribution are build, tested and published instead.

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@main
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
    secrets:
      pypi_password: ${{ secrets.pypi_password }}
```

### Inputs

#### test_extras
Any `extras_requires` modifier that should be used to install the package for testing.
Default is none.

#### test_command
The command to run to test the package.
Will be run in a temporary directory.
Default is no testing.

#### libraries
Packages needed to build the source distribution for testing. Must be a string of space-separated apt packages.
Default is install nothing extra.

#### upload_to_pypi
Whether to always upload to PyPI after successful builds.
If `false`, successful builds are only uploaded when tags are pushed.
Default is `false`.

#### repository_url
The PyPI repository URL to use.
Default is the main PyPI repository.

#### submodules
Whether to checkout submodules.
Default is `true`.

### Secrets

#### pypi_password
The authentication token to access the PyPI repository.
