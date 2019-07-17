#!/usr/local/bin/python3

import oyaml as yaml
import semantic_version
import argparse
import copy
import sys


def parse_args():
    """Load script arguments and return args object"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('file', help='yaml file for version incremental update')
    parser.add_argument('key', help='yaml key that contains version to increment')
    parser.add_argument('--inc_type', default='patch',
                        choices=['major', 'minor', 'patch'],
                        help='incremental type (default: %(default)s)')
    return parser.parse_args()


def load_yaml(file_path):
    """Load yaml file and return yaml object"""
    try:
        f = open(file_path)
    except FileNotFoundError:
        print('ERROR: File', file_path, 'not found!')
        sys.exit(1)
    yaml_obj = yaml.safe_load(f)
    f.close()
    return yaml_obj


def yaml_version_incremental_update(v, incremental):
    """Return a value of incremented version, if version is non-semantic print warning message"""
    try:
        ver = semantic_version.Version((v[1:] if v.startswith('v') else v))
    except Exception:
        print('WARNING: Non-semantic version:', v, 'will not update...')
        return v
    if incremental == 'patch':
        ver = semantic_version.Version.next_patch(ver)
    elif incremental == 'minor':
        ver = semantic_version.Version.next_minor(ver)
    elif incremental == 'major':
        ver = semantic_version.Version.next_major(ver)
    return 'v' + str(ver) if v.startswith('v') else str(ver)


def find_versions(obj, key, incremental):
    """Search recursively for provided key, and increment version if found, return updated dictionary"""
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = find_versions(v, key, incremental)
    if key in obj:
        obj[key] = yaml_version_incremental_update(v, incremental)
        if obj[key] != v:
            print('INFO: Found', key, 'key, incrementing version:', v, '=>', obj[key])
    return obj


def process(file_path, key, incremental):
    """Process input file and write incremental changes"""
    data = load_yaml(file_path)
    data_orig = copy.deepcopy(data)
    find_versions(data, key, incremental)
    if data_orig == data:
        print('Nothing to update...')
    else:
        print('Writing updated yaml...')
        with open(file_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)


def main():
    args = parse_args()
    process(vars(args)['file'], vars(args)['key'], vars(args)['inc_type'])


if __name__ == '__main__':
    main()
