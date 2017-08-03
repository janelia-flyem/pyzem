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

#long_description = read('docs/README.txt', 'docs/CHANGES.txt')
long_description = 'todo'

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name = 'pyzem',
    version = pyzem.__version__,
    url = '',
    author = 'Ting Zhao',
    tests_require = ['pytest'],
    install_requires = [],
    cmdclass = {'test': PyTest},
    author_email = 'tingzhao@gmail.com',
    description = 'Python package for flyem utilities',
    long_description = long_description,
    packages = ['pyzem', 'pyzem.studio', 'pyzem.dvid', 'pyzem.compute'],
    include_package_data = True,
    platforms = 'any',
    test_suite = 'pyzem.test.pyzem',
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
    }
)




