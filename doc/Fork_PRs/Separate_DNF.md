# Added 'html_generate_dnf' to add a separated section for DNF components

- **Pull-request**: [#85](https://github.com/SchrodingersGat/KiBoM/pull/85)
- **Opened**: 2020-03-11
- **Status**: Merged (2020-03-12)

## Description

DNF (Do Not Fit) components are components that are not supposed to be included.
They are usually components used for debug purposes or to implement optional functionality.
These components are marked adding *DNF* to the *Config* field.

They aren't listed in the BoM, but you could want to have a separated list containing them.

This patch adds an option to make the above mentioned list.

## How to use

Set the `html_generate_dnf` option to `1` in the configuration file (i.e. bom.ini)

## Limitations

Only available for HTML output
