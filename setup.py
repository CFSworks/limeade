#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

from limeade import __author__, __version__


author = __author__.split('<',1)[0].strip()
author_email = __author__.split('<',1)[-1].strip('> \t\r\n')


with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r') as f:
    readme = f.read()
    long_description = readme.split('pypi section follows', 1)[1].strip()


setup(
    name='limeade',
    author=author,
    author_email=author_email,
    version=__version__,
    url='https://github.com/CFSworks/limeade',
    description='Library for hot reloading Python code at runtime',
    long_description=long_description,
    license='BSD 3-Clause License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
    packages=find_packages('.', exclude=['tests']),
    zip_safe=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov', 'pytest'],
)
