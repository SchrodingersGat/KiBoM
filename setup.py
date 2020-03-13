#!/usr/bin/python3
import io
import os
import re
import sys
from distutils.core import setup

# Package meta-data.
NAME = 'kibom'
NAME_PKG = 'bomlib'
DESCRIPTION = 'Configurable BoM generation tool for KiCad'
URL = 'https://github.com/INTI-CMNB/KiBoM/'
EMAIL = 'oliver.henry.walters@gmail.com'
AUTHOR = 'Oliver Henry Walters'

here = os.path.abspath(os.path.dirname(__file__))
# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Find the version
with open('KiBOM_CLI.py') as f:
    for line in f:
        z=re.match('KIBOM_VERSION\s+=\s+\"([\d\.]+)\"',line)
        if z:
           version=z.groups()[0]
           break
try:
    print('Version is '+version)
except:
    print('Can\'t find version!')
    sys.exit(1)

setup(name=NAME,
      version=version,
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      packages=[NAME_PKG],
      package_dir={NAME_PKG: NAME_PKG},
      scripts=['KiBOM_CLI.py'],
      install_requires=['xlswriter'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
                   ],
      platforms='POSIX',
      license='MIT'
      )
