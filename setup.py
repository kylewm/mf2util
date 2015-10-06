#!/usr/bin/env python
from distutils.core import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='mf2util',
      version='0.2.7',
      description='Python Microformats2 utilities, a companion to mf2py',
      long_description="""
Microformats2 Utilities
=======================

Microformats2 provides an extremely flexible way to mark up HTML
documents, so that human-centric data is machine-discoverable. This
utility can be used to interpret a microformatted post or event, for
display as a `comment <http://indiewebcamp.com/comments-presentation>`__
or `reply-context <http://indiewebcamp.com/reply-context>`__.

The library itself has no dependencies, but it won't do you much good
without an mf2 parser. I use and recommend
`mf2py <https://github.com/tommorris/mf2py>`__.

Full `documentation is on GitHub
<https://github.com/kylewm/mf2util/blob/master/README.md>`__.

Compatibility: Python 2.6, 2.7, 3.3+

License: `Simplified BSD <http://opensource.org/licenses/BSD-2-Clause>`__
""",
      author='Kyle Mahan',
      author_email='kyle@kylewm.com',
      url='http://indiewebcamp.com/mf2util',
      packages=['mf2util'],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing :: Markup :: HTML'
      ]
  )
