from setuptools import setup, find_packages

setup(
    name='Pyrebase',
    version='0.3.41',
    url='https://github.com/thisbejim/Pyrebase',
    description='A simple python wrapper for the Firebase API',
    author='https://github.com/thisbejim/Pyrebase/graphs/contributors',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests', 'firebase_token_generator']
)
