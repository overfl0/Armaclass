import os
import subprocess
from pathlib import Path

armaclass_path = Path('armaclass')
types = ('*.html', '*.c', '*.cpp', '*.pyd', '*.so')

files_to_delete = []
for file_type in types:
    files_to_delete.extend(armaclass_path.glob(file_type))

for file_path in files_to_delete:
    print('Deleting', file_path)
    os.remove(file_path)

subprocess.run('python setup_cython.py build_ext --inplace --force', shell=True, check=True)
subprocess.run('pytest -x -s', shell=True, check=True)
subprocess.run('python tests/testconfig.py', shell=True, check=True)
