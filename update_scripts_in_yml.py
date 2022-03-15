import os
from base64 import b64encode


def base64_encode_into(script, yml_file, env_var):

    with open(os.path.join('tools', script), 'rb') as f:
        tox_matrix_base64 = b64encode(f.read()).decode('ascii')

    with open(yml_file) as f:
        tox_yml = f.read()

    tox_yml_lines = tox_yml.splitlines()

    for i in range(len(tox_yml_lines)):
        if tox_yml_lines[i].strip().startswith(env_var + ':'):
            pos = tox_yml_lines[i].index(':')
            tox_yml_lines[i] = tox_yml_lines[i][:pos+1] + ' ' + tox_matrix_base64
            break
    else:
        raise ValueError(f'No line containing {env_var} found')

    tox_yml_new = '\n'.join(tox_yml_lines) + '\n'

    with open(yml_file, 'w') as f:
        f.write(tox_yml_new)


base64_encode_into('tox_matrix.py', 'tox.yml', 'TOX_MATRIX_SCRIPT')
base64_encode_into('load_build_targets.py', 'publish.yml', 'LOAD_BUILD_TARGETS_SCRIPT')
