# -*- coding: utf-8 -*-

import setuptools

from kibom.version import KIBOM_VERSION

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="kibom",

    version=KIBOM_VERSION,

    author_email="oliver.henry.walters@gmail.com",

    description="Bill of Materials generation tool for KiCad EDA",

    long_description=long_description,

    long_description_content_type="text/markdown",

    keywords="kicad, bom, electronics, schematic, bill of materials",

    url="https://github.com/SchrodingersGat/KiBom",

    license="MIT",

    packages=setuptools.find_packages(),

    install_requires=[
        "xlsxwriter",
        "colorama",
    ]

    python_requires=">=2.7"
)
