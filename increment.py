#!/usr/local/bin/python3

import oyaml as yaml
import semantic_version
import argparse
import copy

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('file', help='yaml file for version incremental update')
parser.add_argument('key', help='yaml key that contains version to increment')
parser.add_argument('--inc_type', default='patch',
                    choices=['major', 'minor', 'patch'],
                    help='incremental type (default: %(default)s)')
args = parser.parse_args()
yaml_file_name = vars(args)['file']
inc_type = vars(args)['inc_type']
increment_key = vars(args)['key']
yaml_file = open(yaml_file_name)
data = yaml.safe_load(yaml_file)
yaml_file.close()


def increment_version(v, inc_t):
    """Return a value of incremented version, if version is non-semantic print warning message"""
    try:
        ver = semantic_version.Version((v[1:] if v.startswith('v') else v))
    except Exception:
        print('WARNING: Non-semantic version:', v, 'will not update...')
        return v
    if inc_t == 'patch':
        ver = semantic_version.Version.next_patch(ver)
    elif inc_t == 'minor':
        ver = semantic_version.Version.next_minor(ver)
    elif inc_t == 'major':
        ver = semantic_version.Version.next_major(ver)
    return 'v' + str(ver) if v.startswith('v') else str(ver)


def update_dictionary(obj, key):
    """Search recursively for provided key, and increment version if found, return updated dictionary"""
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = update_dictionary(v, key)
    if key in obj:
        obj[key] = increment_version(v, inc_type)
        if obj[key] != v:
            print('INFO: Found', key, 'key, incrementing version:', v, '=>', obj[key])
    return obj


data_orig = copy.deepcopy(data)
update_dictionary(data, increment_key)

if data_orig == data:
    print('Nothing to update...')
else:
    print('Writing updated yaml...')
    with open(yaml_file_name, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
