#!/usr/bin/env python
from distutils.core import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='mf2util',
      version='0.1.5',
      description='Python Microformats2 utilities, a companion to mf2py',
      long_description=readme(),
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
