# github-actions-workflows

Reusable workflows for GitHub Actions.

- [Test a Python package using tox](#test-a-python-package-using-tox)
- [Build and publish a Python package](#build-and-publish-a-python-package)
- [Build and publish a pure Python package](#build-and-publish-a-pure-python-package)

## Test a Python package using tox

This workflow makes it easy to map tox environments to GitHub Actions jobs.
To use this template, your repository will need to have a `tox.ini` file.

```yaml
jobs:
  test:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
    with:
      posargs: '-n 4'
      envs: |
        - linux: pep8
          pytest: false
        - macos: py310
        - windows: py39-docs
          libraries:
            choco:
              - graphviz
      coverage: 'codecov'
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Inputs

A specification of tox environments must be passed to the `envs` input.
There are a number of other inputs.
All of these inputs (except `submodules`) can also be specified under each tox environment to overwrite the global value.

In the following example `test1` will pass `--arg-local` to pytest, while `test2` will pass `--arg-global` to pytest,
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  posargs: '--arg-global'
  envs: |
    - linux: test1
      posargs: '--arg-local'
    - linux: test2
```

#### envs
Array of tox environments to test.
Required input.

```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  envs: |
    - <os>: <toxenv>
    - <os>: <toxenv>
```

where `<os>` is the either `linux`, `macos` or `windows`, and `<toxenv>` is the name of the tox environment to run.

***Note:** `envs` is a **string** and must be specified as a literal block scalar using the `|`. (Without the `|`, it must also be valid YAML.)*

Example:

```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  envs: |
    - linux: pep8
    - linux: py39
    - macos: py38-docs
      name: build_docs
    - windows: py310-conda
```

The name of the GitHub Actions job can be changed with the `name` option as shown above.
By default, `name` will be the name of the tox environment.

#### libraries
Additional packages to install using apt (only on Linux), brew and brew cask (only on macOS), and choco (only on Windows).

Global definition:
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  libraries: |
    apt:
      - package1
      - package2
    brew:
      - package3
    brew-cask:
      - package4
    choco:
      - package5
```

***Note:** `libraries` is a **string** and must be specified as a literal block scalar using the `|`. (Without the `|`, it must also be valid YAML.)*

`envs` definition:
```yaml
with:
  envs: |
    - linux: py39
      libraries:
        apt:
          - package1
```

#### posargs
Positional arguments for the `{posargs}` replacement in an underlying test command within tox.
Default is none.

#### toxdeps
Additional tox dependencies.
This string is included at the end of the `pip install` command when installing tox.
Default is none.

#### toxargs
Positional arguments for tox.
Default is none.

#### pytest
Whether pytest is run by the tox environment.
This determines if additional pytest positional arguments should be passed to tox.
These arguments are to assist with saving test coverage reports.
Default is `true`.

Coverage will not be uploaded if this is `false`.

#### coverage
A space separated list of coverage providers to upload to.
Currently only `codecov` is supported.
Default is to not upload coverage reports.

See also, `CODECOV_TOKEN` secret.

#### conda
Whether to test within a conda environment using `tox-conda`.
Options are `'auto'` (default), `'true'` and `'false'`.

If `'auto'`, conda will be used if the tox environment names contains "conda".
For example, `'auto'` would enable conda for tox environments named `py39-conda`, `conda-test` or even `py38-secondary`.

#### display
Whether to setup a headless display.
This uses the `pyvista/setup-headless-display-action@v1` GitHub Action.
Default is `false`.

#### cache-path
A list of files, directories, and wildcard patterns to cache and restore.
Passed to [`actions/cache`](https://github.com/actions/cache) `path` input.
Optional.

In this example, during the `core_test` job the `sample_data` is retrieved as usual and cached at the end of the job, however, during the `detailed_tests` jobs the `sample_data` is restored from the cache:
```yaml
jobs:
  core_test:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
    with:
      cache-path: sample_data/
      cache-key: sample-${{ github.run_id }}
      envs: |
        - linux: py39
  detailed_tests:
    needs: [core_test]
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
    with:
      cache-path: sample_data/
      cache-key: sample-${{ github.run_id }}
      envs: |
        - macos: py39
        - windows: py39
```

In this example, the particular set of `sample_data` and `processed_data` needed for the job are restored from the cache if the manifest file has not been modified.
As the repository is not checked out when calling the workflow, we need to find the hash of the files in a separate job:
```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      data-hash: ${{ steps.data-hash.outputs.hash }}
      compressed-data-hash: ${{ steps.compressed-data-hash.outputs.hash }}
    steps:
      - uses: actions/checkout@v3
      - id: data-hash
        run: echo "::set-output name=hash::${{ hashFiles('**/data_urls.json') }}"
      - id: compressed-data-hash
        run: echo "::set-output name=hash::${{ hashFiles('**/compressed_data_urls.json') }}"
  tests:
    needs: [setup]
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
    with:
      cache-path: |
        sample_data/
        processed_data/
      envs: |
        - linux: py39
          cache-key: full-sample-${{ needs.setup.outputs.data-hash }}
        - linux: py39-compressed
          cache-key: compressed-sample-${{ needs.setup.outputs.compressed-data-hash }}
```

#### cache-key
An explicit key for restoring and saving the cache.
Passed to [`actions/cache`](https://github.com/actions/cache) `key` input.
Optional.

#### cache-restore-keys
An ordered list of keys to use for restoring the cache if no cache hit occurred for key.
Passed to [`actions/cache`](https://github.com/actions/cache) `restore-keys` input.
Optional.

#### runs-on
Choose an alternative image for the runner to use for each OS.
By default, `linux` is `ubuntu-latest`, `macos` is `macos-latest` and `windows` is `windows-latest`.
None, some or all OS images can be specified, and the global value can be overridden in each environment.

It can be defined globally:
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  runs-on: |
    linux: ubuntu-18.04
    macos: macos-10.15
    windows: windows-2019
```
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  runs-on: |
    macos: macos-10.15
```

***Note:** `runs-on` is a **string** and must be specified as a literal block scalar using the `|`. (Without the `|`, it must also be valid YAML.)*

`envs` definition:
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  envs: |
    - windows: py39
      runs-on: windows-2019
```

#### default_python
The version of Python to use if the tox environment name does not start with `py(2|3)[0-9]+` or `python-version` is not set for the tox environment.
Default is `3.x`.

For example, a tox environment `py39-docs` will run on Python 3.9, while a tox environment `build_docs` will refer to the value of `default_python`.
The `default_python` can also be defined within `envs`, however, a Python version specified in the tox environment name takes priority.

To force a particular Python version for a tox environment, the `python-version` can be included in the definition of the specific environment.
The value of the `python-version` input will override both the Python version in the tox environment name and any `default_python` inputs.
See [`actions/setup-python`](https://github.com/actions/setup-python) for a full list of supported values for `python-version`.
In this example, the development version of Python 3.11 and the PyPy implementation of Python 3.9 will be tested:
```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
with:
  envs: |
    - linux: py311
      python-version: '3.11-dev'
    - linux: pypy39
      python-version: 'pypy-3.9'
```

#### fail-fast
Whether to cancel all in-progress jobs if any job fails.
Default is `false`.

#### submodules
Whether to checkout submodules.
Default is `true`.

### Secrets

#### CODECOV_TOKEN
If your repository is private, in order to upload to Codecov you need to set the `CODECOV_TOKEN` environment variable or pass it as a secret to the workflow.

## Build and publish a Python package

Build, test and publish a Python source distribution and collection of platform-dependent wheels.

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish.yml@v1
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
      targets: |
        - linux
        - cp3?-macosx_x86_64
    secrets:
      pypi_token: ${{ secrets.pypi_token }}
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

#### sdist-runs-on
Choose an alternative image for the runner to use for building and testing the
source distribution. By default, this is `ubuntu-latest`.

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
Whether to upload to PyPI after successful builds.
The default is to upload to PyPI when tags that start with `v` are pushed.
A boolean can be passed as `true` (always upload) or `false` (never upload)
either explicitly or as a boolean expression (`${{ <expression> }}`).

Alternatively, a string can be passed to match the start of a tag ref.
For example, `'refs/tags/v'` (default) will upload tags that begin with `v`,
and `'refs/tags/'` will upload on all pushed tags.

```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
with:
  upload_to_pypi: refs/tags/
```

#### repository_url
The PyPI repository URL to use.
Default is the main PyPI repository.

#### upload_to_anaconda
Whether to upload to Anaconda.org after successful builds.
The default is to not upload.
A boolean can be passed as `true` (always upload) or `false` (never upload)
either explicitly or as a boolean expression (`${{ <expression> }}`).

#### anaconda_user
Anaconda.org user or organisation.
Required if `upload_to_anaconda` is true.

#### fail-fast
Whether to cancel all in-progress jobs if any job fails.
Default is `false`.

#### submodules
Whether to checkout submodules.
Default is `true`.

### Secrets

#### pypi_token
The authentication token to access the PyPI repository.

#### anaconda_token
The authentication token to access the Anaconda.org repository.
This token should have the scope [`api:write`](https://docs.anaconda.com/anaconda-repository/2.23/user/managing-account/#generating-tokens) (allow write access to the API site).

## Build and publish a pure Python package

This the workflow is similar to the `publish.yml` workflow, except, instead of building wheels using cibuildwheel, a pure Python wheel and a source distribution are build, tested and published instead.

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
    secrets:
      pypi_token: ${{ secrets.pypi_token }}
```

### Inputs

#### runs-on
Choose an alternative image for the runner to use for building and testing the
source distribution and wheel. By default, this is `ubuntu-latest`.

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
Whether to upload to PyPI after successful builds.
The default is to upload to PyPI when tags that start with `v` are pushed.
A boolean can be passed as `true` (always upload) or `false` (never upload)
either explicitly or as a boolean expression (`${{ <expression> }}`).

Alternatively, a string can be passed to match the start of a tag ref.
For example, `'refs/tags/v'` (default) will upload tags that begin with `v`,
and `'refs/tags/'` will upload on all pushed tags.

```yaml
uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
with:
  upload_to_pypi: refs/tags/
```

#### repository_url
The PyPI repository URL to use.
Default is the main PyPI repository.

#### upload_to_anaconda
Whether to upload to Anaconda.org after successful builds.
The default is to not upload.
A boolean can be passed as `true` (always upload) or `false` (never upload)
either explicitly or as a boolean expression (`${{ <expression> }}`).

#### anaconda_user
Anaconda.org user or organisation.
Required if `upload_to_anaconda` is true.

#### submodules
Whether to checkout submodules.
Default is `true`.

### Secrets

#### pypi_token
The authentication token to access the PyPI repository.

#### anaconda_token
The authentication token to access the Anaconda.org repository.
This token should have the scope [`api:write`](https://docs.anaconda.com/anaconda-repository/2.23/user/managing-account/#generating-tokens) (allow write access to the API site).
