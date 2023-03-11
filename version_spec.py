class VersionSpec:
    def __init__(self, ranges):
        self.ranges = ranges

    @staticmethod
    def parse(pattern):
        if isinstance(pattern ,list):
            ranges = [parse_range(string) for string in pattern]
        elif isinstance(pattern, str):
            ranges = [parse_range(pattern)]
        else:
            raise ValueError('must be str or list')
        return VersionSpec(ranges)

    def __str__(self):
        inf = float('inf')
        if len(self.ranges) == 1 and self.ranges[0][0] == (0, 0, 0) and self.ranges[0][1] == (inf, inf, inf):
            s = '*'
        else:
            s = ', '.join([range_to_str(r[0], r[1]) for r in self.ranges])
        return s

    def __contains__(self, version):
        v = parse_version(version)
        for lower, upper in self.ranges:
            if lower <= v <= upper:
                return True
        return False


def parse_range(string):
    if '-' in string:
        lower, upper = string.split('-')
    else:
        lower = string
        upper = string
    lower = parse_version(lower, default=0)
    upper = parse_version(upper, default=float('inf'))
    rng = (lower, upper)
    return rng


def parse_version(string, default=None):
    n = string.count('.')
    if default is None and n != 2:
        raise ValueError('if default is None a version number must be in the format x.y.z')
    if default == float('inf') and string == '*':
        major = default
        minor = default
        patch = default
    else:
        if n == 0:
            major = int(string)
            minor = default
            patch = default
        elif n == 1:
            first, second = string.split('.')
            major = int(first)
            minor = int(second)
            patch = default
        elif n == 2:
            first, second, third = string.split('.')
            major = int(first)
            minor = int(second)
            patch = int(third)
        else:
            raise ValueError(f'invalid version: {string}')
    version = (major, minor, patch)
    return version


def range_to_str(lower, upper):
    if lower == upper:
        s = version_to_str(lower)
    else:
        s = f'{version_to_str(lower)} - {version_to_str(upper)}'
    return s


def version_to_str(t):
    return '.'.join(['*' if n == float('inf') else str(n) for n in t])
