# Component description fallback for KiCad 5.x

- **Pull-request**: [#78](https://github.com/SchrodingersGat/KiBoM/pull/78)
- **Opened**: 2020-03-11
- **Status**: Merged (2020-03-12)

## Description

The description for a component is obtained from the component entry in the netlist.

When this description is absent the code looks for the description of the component in the library.

The old code did it only for KiCad 4.x netlists, this patch adds it also for KiCad 5.x components.

