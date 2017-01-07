from setuptools import setup, find_packages

setup(
    name='Pyrebase',
    version='3.0.27',
    url='https://github.com/thisbejim/Pyrebase',
    description='A simple python wrapper for the Firebase API',
    author='James Childs-Maidment',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests==2.11.1',
        'gcloud==0.17.0',
        'oauth2client==3.0.0',
        'requests_toolbelt==0.7.0',
        'python_jwt==2.0.1',
        'pycryptodome==3.4.3'
    ]
)
