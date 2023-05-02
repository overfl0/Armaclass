rem ptw --beforerun "del armaclass\*.c && python setup.py build_ext --inplace"

set -x
del armaclass\*.c* armaclass\*.pyd armaclass\*.html
python setup.py build_ext --inplace --force

pytest -x -s
python testconfig.py
