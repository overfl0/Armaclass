Checklist to push a release to PyPi:

* Run tests
* Update version in setup.py
* git tag
* git push
* git push --tag
* python setup.py sdist
* twine upload --repository-url https://test.pypi.org/legacy/ dist/*
* twine upload dist/something
