# -*- coding: utf-8 -*-

import setuptools

import os
import sys
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)
print(here)
#sys.path.append(os.path.join(here, "KiBOM"))

from kibom.version import KIBOM_VERSION

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="kibom",

    version=KIBOM_VERSION,

    author = "Oliver Henry Walters",

    author_email="oliver.henry.walters@gmail.com",

    description="Bill of Materials generation tool for KiCad EDA",

    long_description=long_description,

    long_description_content_type="text/markdown",

    keywords="kicad, bom, electronics, schematic, bill of materials",

    url="https://github.com/INTI-CMNB/KiBoM/",

    license="MIT",

    packages=setuptools.find_packages(),
    #packages=['bomlib'],
    #package_dir={'bomlib': 'bomlib'},

    scripts=['KiBOM_CLI.py'],

    install_requires=[
        "xlsxwriter",
        "colorama",
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],

    python_requires=">=3.2"
)
