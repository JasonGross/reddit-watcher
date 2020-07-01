#!/usr/bin/env python3
import watch_version

if __name__ == '__main__':
    major, minor, revision = watch_version.MAJOR, watch_version.MINOR, watch_version.REVISION
    with open('watch_version.py', 'w') as f:
        f.write(f'''MAJOR = {major}
MINOR = {minor}
REVISION = {revision+1}
''')
