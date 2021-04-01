Checklist to push a release to PyPi:

* Run tests
* Update version in setup.py
* git tag
* git push
* git push --tag
* python setup.py sdist
* twine upload dist/something
