# Remove the path in getSource

- **Pull-request**: [#86](https://github.com/SchrodingersGat/KiBoM/pull/86)
- **Opened**: 2020-03-12
- **Status**: Closed by [#90](https://github.com/SchrodingersGat/KiBoM/pull/90) (2020-03-12). Same patch but adapted to support Windows details.

## Description

The *Source File* entry of the output contained the name of the schematic and its path.
There is no point in exposing your local path to your client or the rest of the world.

This patch suppressed the path.
