
from setuptools import setup, find_packages

setup(
    name='Pyrebase',
    version='0.2.932',
    url='https://github.com/thisbejim/Pyrebase',
    description='A simple python wrapper for the Firebase API',
    author='James Childs-Maidment',
    author_email='jchildsmaidment@outlook.com',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
    ],

    keywords='Firebase',

    packages=find_packages(exclude=['test']),
    install_requires=['requests_futures','firebase_token_generator'],
    package_dir={'requests': 'requests'}
)
