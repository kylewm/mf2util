#!/usr/bin/env python
from distutils.core import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(name='mf2util',
      version='0.1.0',
      description='Python Microformats2 utilities',
      long_description='Companion package for mf2py microformats2 parser. Provides utility functions to interpret post permalinks for display as comments or reply-context',
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
