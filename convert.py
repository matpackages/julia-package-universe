import sys
import os
import toml
import json
from version_spec import VersionSpec


def main():
    registry_path = 'General'
    output_file = sys.argv[1]
    registry_file = os.path.join(registry_path, 'Registry.toml')
    ignore = ['julia']
    paths = read_package_paths(registry_file, ignore)
    packages = {}
    for name, path in paths.items():
        packages[name] = read_package_data(os.path.join(registry_path, path))
    write_json(output_file, packages)


def read_package_paths(registry_file, ignore):
    registry_data = read_toml(registry_file)
    packages = registry_data['packages']
    paths = {}
    for val in packages.values():
        name = val['name']
        if name not in ignore:
            path = val['path']
            paths[name] = path
    return paths


def read_package_data(path):
    deps_file = os.path.join(path, 'Compat.toml')
    versions_file = os.path.join(path, 'Versions.toml')
    deps = read_toml(deps_file)
    deps = convert_dependencies(deps)
    versions = read_versions(versions_file)
    data = {}
    for version in versions:
        data[version] = get_dependencies(deps, version)
    return data


def read_versions(file):
    data = read_toml(file)
    versions = []
    for v in data.keys():
        ver = v
        for char in ['-', '+']:
            if char in ver:
                p = ver.index(char)
                ver = ver[0:p]
        versions.append(ver)
    versions = list(set(versions))
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    return versions


def convert_dependencies(deps):
    d = {}
    for range, dependencies in deps.items():
        r = VersionSpec.parse(range)
        dep = {}
        for name, spec in dependencies.items():
            dep[name] = str(VersionSpec.parse(spec))
        d[r] = dep
    return d


def get_dependencies(deps, version):
    d = {}
    for range, dependencies in deps.items():
        if version in range:
            for name, spec in dependencies.items():
                if name in d:
                    raise ValueError('dependency already exists')
                d[name] = spec
    return d


def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)


def read_toml(file):
    with open(file, 'r') as f:
        data = toml.load(f)
    return data


if __name__ == '__main__':
    main()
