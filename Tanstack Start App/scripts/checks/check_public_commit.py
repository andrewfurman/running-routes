#!/usr/bin/env python3
"""Block environment files and recognizable credential values in public commits."""
import re
import subprocess
import sys
all_files = '--all' in sys.argv
cmd = ['git', 'ls-files', '-z'] if all_files else ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z']
paths = subprocess.check_output(cmd).decode().split('\0')
patterns = [rb'AIza[0-9A-Za-z_-]{30,}', rb'cfat_[A-Za-z0-9_-]{20,}', rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'GOCSPX-[A-Za-z0-9_-]{15,}', rb'1//[A-Za-z0-9_-]{40,}']
errors = []
for path in filter(None, paths):
    if path.rsplit('/', 1)[-1].startswith('.env') or path.rsplit('/', 1)[-1] in {'sample.env', '.dev.vars'}:
        errors.append(path + ': environment files must stay uncommitted')
        continue
    data = subprocess.check_output(['git', 'show', ':' + path])
    if any(re.search(pattern, data) for pattern in patterns):
        errors.append(path + ': possible credential value')
if errors:
    print('\n'.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('Public commit check passed')
