import sys
import os
import toml
import json
from version_spec import VersionSpec


def main():
    registry_path = 'General'
    output_file = sys.argv[1]
    registry_file = os.path.join(registry_path, 'Registry.toml')
    paths = read_package_paths(registry_file)
    paths['Pkg'] = ''
    packages = {}
    names = sorted(paths.keys())
    julia_versions = read_julia_versions('julia-versions.txt')
    pkg_versions = read_julia_versions('pkg-versions.txt')
    for name in names:
        if name == 'julia':
            p = {v: {} for v in julia_versions}
        elif name == 'Pkg':
            p = {v: {} for v in pkg_versions}
        else:
            p = read_package_data(os.path.join(registry_path, paths[name]))
        packages[name] = p
    write_json(output_file, packages)


def read_package_paths(registry_file):
    registry_data = read_toml(registry_file)
    packages = registry_data['packages']
    paths = {}
    for val in packages.values():
        name = val['name']
        path = val['path']
        paths[name] = path
    return paths


def read_package_data(path):
    deps_file = os.path.join(path, 'Deps.toml')
    compat_file = os.path.join(path, 'Compat.toml')
    versions_file = os.path.join(path, 'Versions.toml')
    deps = read_toml(deps_file) if os.path.isfile(deps_file) else {}
    compat = read_toml(compat_file)
    deps = merge_deps_compat(deps, compat)
    deps = convert_dependencies(deps)
    versions = read_versions(versions_file)
    data = {}
    for version in versions:
        data[version] = get_dependencies(deps, version)
    return data


def read_versions(file):
    data = read_toml(file)
    versions = pure_versions(data.keys())
    return versions


def pure_versions(vers):
    versions = []
    for v in vers:
        versions.append(pure_semver(v))
    versions = list(set(versions))
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    return versions


def pure_semver(v):
    ver = v
    for char in ['-', '+']:
        if char in ver:
            p = ver.index(char)
            ver = ver[0:p]
    return ver


def merge_deps_compat(deps, compat):
    d = {}
    for range, dependencies in deps.items():
        dep = {}
        for name in dependencies.keys():
            dep[name] = '*'
        d[range] = dep
    for range, dependencies in compat.items():
        dep = d[range] if range in d else {}
        for name, spec in dependencies.items():
            dep[name] = spec
        d[range] = dep
    return d


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
                    if d[name] == '*' and spec != '*':
                        pass
                    elif d[name] != '*' and spec == '*':
                        spec = d[name]
                    else:
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


def read_julia_versions(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    versions = []
    for line in lines:
        if line.startswith('v'):
            v = line[1:]
        else:
            v = line
        if v.count('.') == 2:
            versions.append(v.strip())
    return pure_versions(versions)


if __name__ == '__main__':
    main()
