import sys
import os
import toml


def main():
    registry_path = 'General'
    output_file = sys.argv[1]
    registry_file = os.path.join(registry_path, 'Registry.toml')
    with open(registry_file, 'r') as f:
        registry_data = toml.load(f)
    print('done')


if __name__ == '__main__':
    main()
