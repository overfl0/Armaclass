Checklist to push a release to PyPi:

* Run tests
* Update version in setup.py
* git tag
* git push
* git push --tag
* python setup.py sdist
* python setup.py bdist_wheel --universal
* twine upload --repository armaclass_test dist/*
* twine upload --repository armaclass dist/*
