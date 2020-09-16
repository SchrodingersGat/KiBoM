# -*- coding: utf-8 -*-

import setuptools

from kibom.version import KIBOM_VERSION

long_description = "KiBoM is a configurable BOM (Bill of Materials) generation tool for KiCad EDA. Written in Python, it can be used directly with KiCad software without the need for any external libraries or plugins. KiBoM intelligently groups components based on multiple factors, and can generate BoM files in multiple output formats. For futher information see the KiBom project page"


setuptools.setup(
    name="kibom",
    version=KIBOM_VERSION,
    author="Oliver Walters",
    author_email="oliver.henry.walters@gmail.com",
    description="Bill of Materials generation tool for KiCad EDA",
    long_description=long_description,
    keywords="kicad, bom, electronics, schematic, bill of materials",
    url="https://github.com/SchrodingersGat/KiBom",
    license="MIT",
    packages=setuptools.find_packages(),
    scripts=['KiBOM_CLI.py'],
    entry_points={
        'console_scripts': ['kibom = kibom.__main__:main']
    },
    install_requires=[
        "xlsxwriter",
    ],
    python_requires=">=2.7"
)
