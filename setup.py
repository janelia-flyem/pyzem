from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import pyzem

here = os.path.abspath(os.path.dirname(__file__))

#Read multiple files and return their concatenation
def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [l for l in requirements if not l.strip().startswith('#')]

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pyzem',
    version = pyzem.__version__,
    url = '',
    author = pyzem.__author__,
    tests_require = ['pytest'],
    install_requires = requirements,
    # install_requires = ['numpy', 'requests', 'timer', 'networkx', 'bottle', 'anytree'],
    cmdclass = {'test': PyTest},
    author_email = pyzem.__email__,
    description = 'Python package for flyem utilities',
    long_description = long_description,
    packages = ['pyzem', 'pyzem.studio', 'pyzem.dvid', 'pyzem.compute', 'pyzem.swc', 'pyzem.tests', 'pyzem.cli'],
    include_package_data = True,
    platforms = 'any',
    # test_suite = 'pyzem.test.pyzem',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 0 - Start',
        'Natural Language :: English',
        'Environment :: ',
        'Intended Audience :: Developers',
        'License :: '
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require = {
        'testing': ['pytest'],
    },
    entry_points = {
        'console_scripts': [
            'process_annotation=pyzem.cli.process_annotation:run'
        ]
    }
)




