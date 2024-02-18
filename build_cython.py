import glob
import os
import subprocess
from itertools import chain

armaclass_path = 'armaclass'
types = ('*.html', '*.c', '*.cpp', '*.pyd', '*.so')
files_to_delete = chain(*(glob.glob(os.path.join(armaclass_path, file_type)) for file_type in types))
for file_path in files_to_delete:
    os.remove(file_path)

subprocess.run('python setup_cython.py build_ext --inplace --force', shell=True, check=True)
subprocess.run('pytest -x -s', shell=True, check=True)
subprocess.run('python testconfig.py', shell=True, check=True)
