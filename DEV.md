Developing
==========

Create a new virtualenv and install the required libraries for
the default pyrebase + the testing tools.

```
mkvirtualenv -p python3 pyrebase-dev # if you have virtualenvwrapper installed
pip install -r requirements.txt -r requirements.dev.txt
```

Configure a test database

```
cp ~/my_secret_firebase_service_account_key.json ./secret.json
cp ./tests/config.template.py ./tests/config.py
# Update the ./tests/config.py file with your test database.
```

Note that to make it easier to run the tests, they read/write to
`/pyrebase_tests/` on your firebase database. They should not mess
up the rest of the database.


Run the tests:

```
pytest -s tests
```

On MacOS you may need to fix the shebang in the pytest executable
to make it point to the correct python binary.

Building
========

1. Install/Update build dependencies:
`pip install --upgrade pip setuptools wheel twine`
1. Increment the version number in setup.py
1. Create the package files:
`python setup.py sdist bdist_wheel`
1. Upload to test pypi repo:
`twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
1. Check that package installs and works in another project:
`pip install --index-url https://test.pypi.org/simple/ pyrebase4==[new version]`
1. Upload to main pypi repo:
`twine upload dist/*`

NOTE: Registration for https://test.pypi.org is separate from https://pypi.org