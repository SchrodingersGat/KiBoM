# -*- coding: utf-8 -*-

import setuptools

import os
import sys
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

from kibom.version import KIBOM_VERSION  # noqa: E402

long_description = "KiBoM is a configurable BOM (Bill of Materials) generation tool for KiCad EDA. Written in Python, it can be used directly with KiCad software without the need for any external libraries or plugins. KiBoM intelligently groups components based on multiple factors, and can generate BoM files in multiple output formats. For futher information see the KiBom project page"


setuptools.setup(
    name="kibom",

    version=KIBOM_VERSION,

    author="Oliver Walters",

    author_email="oliver.henry.walters@gmail.com",

    description="Bill of Materials generation tool for KiCad EDA",

    long_description=long_description,

    keywords="kicad, bom, electronics, schematic, bill of materials",

    url="https://github.com/INTI-CMNB/KiBoM/",

    license="MIT",

    packages=setuptools.find_packages(),

    scripts=['KiBOM_CLI.py'],

    install_requires=[
        "xlsxwriter",
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
