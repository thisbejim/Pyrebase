from setuptools import setup, find_packages

setup(
    name='Pyrebase',
    version='3.1.0',
    url='https://github.com/digitake/Pyrebase',
    description='A forked of thisbejim of a simple python wrapper for the Firebase API',
    author='Digitake',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests==2.20.9',
        'gcloud==0.18.3',
        'oauth2client==4.1.3',
        'requests_toolbelt==0.8.0',
        'python_jwt==3.2.3',
        'pycryptodome==3.7.0'
    ]
)
