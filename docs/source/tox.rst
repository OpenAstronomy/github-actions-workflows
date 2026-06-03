.. _oa-ghaw-tox:

Test a Python package using tox
-------------------------------

This workflow makes it easy to map tox environments to GitHub Actions
jobs. To use this template, your repository will need to have a
``tox.ini`` file.

.. code:: yaml

   jobs:
     test:
       uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
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

Inputs
~~~~~~

A specification of tox environments must be passed to the ``envs``
input. There are a number of other inputs. All of these inputs (except
``submodules`` and ``working-directory``) can also be specified under each tox environment to
overwrite the global value.

In the following example ``test1`` will pass ``--arg-local`` to pytest,
while ``test2`` will pass ``--arg-global`` to pytest,

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     posargs: '--arg-global'
     envs: |
       - linux: test1
         posargs: '--arg-local'
       - linux: test2

envs
^^^^

Array of tox environments to test. Required input.

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - <os>: <toxenv>
       - <os>: <toxenv>

where ``<os>`` is the either ``linux``, ``macos`` or ``windows``, and
``<toxenv>`` is the name of the tox environment to run.

**Note:** ``envs`` is a *string* and must be specified as a literal
block scalar using the ``|``. (Without the ``|``, it must also be valid
YAML.)

Example:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - linux: pep8
       - linux: py39
       - macos: py38-docs
         name: build_docs

The name of the GitHub Actions job can be changed with the ``name``
option as shown above. By default, ``name`` will be the name of the tox
environment.

If the Python version includes a ``t`` suffix, such as ``py313t``, then
a free-threaded Python interpreter will be used.

Python Version Globs (``py*``)
""""""""""""""""""""""""""""""

You can use glob syntax for the Python version (i.e. ``py3*``) to expand into all active (not end-of-life) minor versions of Python retrieved from https://endoflife.date

Additionally, if your project has a ``pyproject.toml`` with a ``project.requires-python`` the Python versions will be constrained to respect that.

For example:
- ``py*`` for all active minor versions of Python supported by your package
- ``py3*`` for all active minor versions of Python 3 supported by your package
- ``py31*`` for all active minor versions of Python between ``3.10`` and ``3.19`` supported by your package

libraries
^^^^^^^^^

Additional packages to install using apt (only on Linux), brew and brew
cask (only on macOS), and choco (only on Windows).

Global definition:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
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

**Note:** ``libraries`` is a *string* and must be specified as a
literal block scalar using the ``|``. (Without the ``|``, it must also
be valid YAML.)

``envs`` definition:

.. code:: yaml

   with:
     envs: |
       - linux: py39
         libraries:
           apt:
             - package1

posargs
^^^^^^^

Positional arguments for the ``{posargs}`` replacement in an underlying
test command within tox. Default is none.

toxdeps
^^^^^^^

Additional tox dependencies. This string is included at the end of the
``pip install`` command when installing tox. Default is none. For example,
to leverage the `uv <https://github.com/astral-sh/uv>`__ package manager you can specify
``toxdeps: tox-uv`` to use the `tox-uv <https://github.com/tox-dev/tox-uv>`__ plugin.

toxargs
^^^^^^^

Positional arguments for tox. Default is none.

pytest
^^^^^^

Whether pytest is run by the tox environment. This determines if
additional pytest positional arguments should be passed to tox. These
arguments are to assist with saving test coverage reports. Default is
``true``.

pytest-results-summary
^^^^^^^^^^^^^^^^^^^^^^

Whether test results from pytest are shown in the
`$GITHUB_STEP_SUMMARY <https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/>`__.
Default is ``false``.

This option has no effect if ``pytest`` is ``false``.

coverage
^^^^^^^^

The coverage option controls how coverage reports are made and processed after the tox job has completed.
The default is to not upload coverage reports.
This option has no effect if ``pytest`` is ``false``.
This option takes a space separated list of coverage providers to upload to, either ``codecov``, ``codecov-oidc``, or ``github``.

As the workflows do not control how your tests are run, configuring coverage correctly may require changes to your tox.ini.
The coverage collection is done inside the tox job, but the workflows handle generating reports and uploading to either codecov or github.

Coverage Collection
###################

There are two main ways to generate coverage for your test run(s):

* Using `coverage.py <https://coverage.readthedocs.io>`__ directly, which generally means prefixing your pytest command with ``coverage run -m <pytest ...>``. This will generate one or more ``.coverage`` files in the current directory (for parallel jobs it can generate one per process).
* Using `pytest-cov <https://pytest-cov.readthedocs.io>`__ which generally involves installing ``pytest-cov`` and adding ``--cov=<packagename>`` to your pytest flags, this will also generate a ``.coverage`` file in the current directory as well as reporting coverage to the terminal by default.

Coverage Reporting
##################

After coverage has been collected the workflows work with collected ``.coverage`` database files that should have been generated as part of your test run.
If uploading to GitHub all these reports will be collected for all your jobs and combined together in a job at the end of the workflow.
If uploading to codecov they will be combined and uploaded at the end of each job.

Both of these report uploads require the ``.coverage`` file(s) to be in the root of the GitHub Actions workspace for processing at the end of the job.

**If you are running your tests in a temporary directory**, more configuration may be required to configure the coverage collection correctly.

The first step is to write the ``.coverage`` file to the same dir as the ``tox.ini`` to do this set the following option in your tox.ini::

  setenv =
      COVERAGE_FILE={toxinidir}/.coverage

This should work for both ``coverage.py`` and ``pytest-cov``.

The next thing you may need to configure is `source mapping <https://coverage.readthedocs.io/en/latest/config.html#config-paths>`__ to map the source code in the temporary directory to the source code in the repository checkout.
This is normally only needed when using ``coverage: github`` as the report is generated in a separate Github Actions job meaning the temporary directory is no longer present.

An example of this is in the ``.coveragerc`` file::

  [paths]
  source =
    test_package/
    .tox/**/test_package

.. _codecov-auth:

Authenticating with Codecov
###########################

There are two supported ways to authenticate with Codecov, either using a ``CODECOV_TOKEN`` or using `OIDC <https://docs.github.com/en/actions/concepts/security/openid-connect>`__.

To use the token set the ``CODECOV_TOKEN`` environment variable or pass it as a secret to the workflow, and set ``coverage: codecov``.
To use oidc you need to give the job the ``id-token: write`` permission, we recommend you set this on the job level not the workflow level, and set ``coverage: codecov-oidc``.


conda_packages
^^^^^^^^^^^^^^

If populated, will set up a conda environment and install the requested packages from ``conda-forge``.
 
Remember to use ``allowlist_externals`` in your Tox configuration if using non-Python Conda packages.

conda_channels
^^^^^^^^^^^^^^

Conda channel(s) to use with ``conda_packages`` (defaults to ``conda-forge``).
If multiple, make sure they're separated by commas.

setenv
^^^^^^

A map of environment variables to be available when testing. Default is
none.

Global definition:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     setenv: |
       VAR1: test
       VAR2: |
         first line
         seconds line
       VAR3: testing

**Note:** ``setenv`` is a *string* and must be specified as a
literal block scalar using the ``|``. (Without the ``|``, it must also
be valid YAML.)

``envs`` definition:

.. code:: yaml

   with:
     envs: |
       - linux: py39
         setenv: |
           VAR1: test
           VAR2: |
             first line
             seconds line
           VAR3: testing

display
^^^^^^^

Whether to setup a headless display. This uses the
``pyvista/setup-headless-display-action@v1`` GitHub Action. Default is
``false``.

cache-path
^^^^^^^^^^

A list of files, directories, and wildcard patterns to cache and
restore. Passed to
https://github.com/actions/cache ``path`` input.
Optional.

In this example, during the ``core_test`` job the ``sample_data`` is
retrieved as usual and cached at the end of the job, however, during the
``detailed_tests`` jobs the ``sample_data`` is restored from the cache:

.. code:: yaml

   jobs:
     core_test:
       uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
       with:
         cache-path: sample_data/
         cache-key: sample-${{ github.run_id }}
         envs: |
           - linux: py39
     detailed_tests:
       needs: [core_test]
       uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
       with:
         cache-path: sample_data/
         cache-key: sample-${{ github.run_id }}
         envs: |
           - macos: py39
           - windows: py39

In this example, the particular set of ``sample_data`` and
``processed_data`` needed for the job are restored from the cache if the
manifest file has not been modified. As the repository is not checked
out when calling the workflow, we need to find the hash of the files in
a separate job:

.. code:: yaml

   jobs:
     setup:
       runs-on: ubuntu-latest
       outputs:
         data-hash: ${{ steps.data-hash.outputs.hash }}
         compressed-data-hash: ${{ steps.compressed-data-hash.outputs.hash }}
       steps:
         - uses: actions/checkout@v3
         - id: data-hash
           run: echo "hash=${{ hashFiles('**/data_urls.json') }}" >> $GITHUB_OUTPUT
         - id: compressed-data-hash
           run: echo "hash=${{ hashFiles('**/compressed_data_urls.json') }}" >> $GITHUB_OUTPUT
     tests:
       needs: [setup]
       uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
       with:
         cache-path: |
           sample_data/
           processed_data/
         envs: |
           - linux: py39
             cache-key: full-sample-${{ needs.setup.outputs.data-hash }}
           - linux: py39-compressed
             cache-key: compressed-sample-${{ needs.setup.outputs.compressed-data-hash }}

cache-key
^^^^^^^^^

An explicit key for restoring and saving the cache. Passed to
https://github.com/actions/cache ``key`` input.
Optional.

cache-restore-keys
^^^^^^^^^^^^^^^^^^

An ordered list of keys to use for restoring the cache if no cache hit
occurred for key. Passed to
https://github.com/actions/cache
``restore-keys`` input. Optional.

artifact-path
^^^^^^^^^^^^^

A list of files, directories, and wildcard patterns to upload as
artifacts. Passed to https://github.com/actions/upload-artifact
``path`` input. Optional.

It can be defined globally:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     artifact-path: path/output/bin/

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     artifact-path: |
       path/output/bin/
       path/output/test-results
       !path/**/*.tmp

``envs`` definition:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - windows: py39
         artifact-path: |
           path/output/bin/
           path/output/test-results
           !path/**/*.tmp

artifact-archive
^^^^^^^^^^^^^^^^

Whether to archive (zip) artifacts when uploading. Default is ``true``.

When ``true``, artifacts are zipped (used to be the only option).
When ``false``, artifacts are not zipped and wildcard patterns are not
supported in ``artifact-path`` (only a single artifact can be
uploaded).

Passed to https://github.com/actions/upload-artifact ``archive`` input.
See `the announcement blog post <https://github.blog/changelog/2026-02-26-github-actions-now-supports-uploading-and-downloading-non-zipped-artifacts/>`__ for more details.

It can be defined globally:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     artifact-path: output.txt
     artifact-archive: false

or specific to an env:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - linux: py39
         artifact-path: output.txt
         artifact-archive: false

artifact-include-hidden-files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Whether to include hidden files (files starting with ``.``) in artifact uploads.
Default is ``false``.

Passed to https://github.com/actions/upload-artifact ``include-hidden-files`` input.

It can be defined globally:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     artifact-path: output/
     artifact-include-hidden-files: true

or specific to an env:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - linux: py39
         artifact-path: output/
         artifact-include-hidden-files: true

artifact-if-no-files-found
^^^^^^^^^^^^^^^^^^^^^^^^^^

The behavior if no files are found at the specified ``artifact-path``.
Options are ``warn`` (default), ``error``, or ``ignore``.

- ``warn``: Output a warning but do not fail the action
- ``error``: Fail the action with an error message
- ``ignore``: Do not output any warnings or errors

Passed to https://github.com/actions/upload-artifact ``if-no-files-found`` input.

It can be defined globally:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     artifact-path: output/
     artifact-if-no-files-found: error

or specific to an env:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - linux: py39
         artifact-path: output/
         artifact-if-no-files-found: ignore

runs-on
^^^^^^^

Choose an alternative image for the runner to use for each OS. By
default, ``linux`` is ``ubuntu-latest``, ``macos`` is ``macos-latest``
and ``windows`` is ``windows-latest``. None, some or all OS images can
be specified, and the global value can be overridden in each
environment.

It can be defined globally:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     runs-on: |
       linux: ubuntu-18.04
       macos: macos-10.15
       windows: windows-2022

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     runs-on: |
       macos: macos-10.15

**Note:** ``runs-on`` is a *string* and must be specified as a
literal block scalar using the ``|``. (Without the ``|``, it must also
be valid YAML.)

``envs`` definition:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - windows: py39
         runs-on: windows-2022

default_python
^^^^^^^^^^^^^^

The version of Python to use if the tox environment name does not start
with ``py(2|3)[0-9]+`` or ``python-version`` is not set for the tox
environment. Default is ``3.x``.

For example, a tox environment ``py39-docs`` will run on Python 3.9,
while a tox environment ``build_docs`` will refer to the value of
``default_python``. The ``default_python`` can also be defined within
``envs``, however, a Python version specified in the tox environment
name takes priority.

To force a particular Python version for a tox environment, the
``python-version`` can be included in the definition of the specific
environment. The value of the ``python-version`` input will override
both the Python version in the tox environment name and any
``default_python`` inputs. See
https://github.com/actions/setup-python
for a full list of supported values for ``python-version``. In this
example, the development version of Python 3.11 and the PyPy
implementation of Python 3.9 will be tested:

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     envs: |
       - linux: py311
         python-version: '3.11-dev'
       - linux: pypy39
         python-version: 'pypy-3.9'

fail-fast
^^^^^^^^^

Whether to cancel all in-progress jobs if any job fails. Default is
``false``.

timeout-minutes
^^^^^^^^^^^^^^^

The maximum number of minutes to let a job run before GitHub
automatically cancels it. Default is ``360``.

submodules
^^^^^^^^^^

Whether to checkout submodules. Default is ``true``.

working-directory
^^^^^^^^^^^^^^^^^

The working directory for running tox, relative to the repository root.
Default is ``.`` (the repository root).

This is useful when your package is located in a subdirectory of the
repository, such as in monorepos where multiple packages exist in the
same repository, or when using a non-standard project layout.

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v2
   with:
     working-directory: packages/my-package
     envs: |
       - linux: py312
