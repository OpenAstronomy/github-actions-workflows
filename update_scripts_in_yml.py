#!/usr/bin/env python

import os
from base64 import b64encode


def base64_encode_into(script, yml_file, env_var):

    with open(os.path.join('tools', script), 'rb') as f:
        tox_matrix_base64 = b64encode(f.read()).decode('ascii')

    with open(os.path.join('.github', 'workflows', yml_file)) as f:
        tox_yml = f.read()

    tox_yml_lines = tox_yml.splitlines()

    updated = False
    for i in range(len(tox_yml_lines)):
        if tox_yml_lines[i].strip().startswith(env_var + ':'):
            pos = tox_yml_lines[i].index(':')
            tox_yml_lines[i] = tox_yml_lines[i][:pos+1] + ' ' + tox_matrix_base64
            updated = True
    if not updated:
        raise ValueError(f'No line containing {env_var} found')

    tox_yml_new = '\n'.join(tox_yml_lines) + '\n'

    with open(os.path.join('.github', 'workflows', yml_file), 'w') as f:
        f.write(tox_yml_new)


base64_encode_into('tox_matrix.py', 'tox.yml', 'TOX_MATRIX_SCRIPT')
base64_encode_into('load_build_targets.py', 'publish.yml', 'LOAD_BUILD_TARGETS_SCRIPT')
base64_encode_into('set_env.py', 'tox.yml', 'SET_ENV_SCRIPT')
base64_encode_into('set_env.py', 'publish.yml', 'SET_ENV_SCRIPT')
base64_encode_into('set_env.py', 'publish_pure_python.yml', 'SET_ENV_SCRIPT')
