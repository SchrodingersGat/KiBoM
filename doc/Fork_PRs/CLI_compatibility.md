# Recover the KiBOM_CLI.py script

- **Pull-request**: [#104](https://github.com/SchrodingersGat/KiBoM/pull/104)
- **Opened**: 2020-07-15
- **Status**: Open

## Description

In version 1.7.0 the KiBOM code was adapted to be a pure Python module, allowing the following use:

```
python -m kibom ...
```

But older versions used:

```
KiBOM_CLI.py ...
```

This patch adds `KiBOM_CLI.py` without compromising the module usage.
The script is provided and declared in `setup.py`.

