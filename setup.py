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
        'requests',
        'gcloud',
        'oauth2client',
        'requests_toolbelt',
        'python_jwt',
        'pycryptodome'
    ]
)
