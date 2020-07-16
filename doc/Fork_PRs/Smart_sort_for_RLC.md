# Modified the R/L/C sort to try to make sense of the multiplier

- **Pull-request**: [#82](https://github.com/SchrodingersGat/KiBoM/pull/82)
- **Opened**: 2020-03-11
- **Status**: Open

## Description

It helps to get 5 pF before 1 nF.

The original search is alphabetic, making *1 nF* to be *smaler* than *5 pF*.
This patch interprets *5 pF* as 5000 and *1 nF* as 1000000 (fempto Farad).

Valid **C** units are: (base is fempto Farad)

- **uF**: 1000000000
- **nF**: 1000000
- **pF**: 1000

Examples:

- 4 uF = 4000000000
- 3.3 nF = 3300000
- 2pf = 2000

Valid **L** units are: (base is fempto Henry)

- **uH**: 1000000000
- **nH**: 1000000
- **pH**: 1000

Examples:

- 4 uH = 4000000000
- 3.3 nH = 3300000
- 2ph = 2000

Valid **R** units are: (base is mili Ohm)

- **M**: 1000000000
- **K**: 1000000
- **R**: 1000

Examples:

- 4.7 = 4700
- 2k2 = 2200000
- 3R3 = 3300
- 10K = 10000000

## How to use

Just use the propper units and multipliers.

## Limitations

Not all possible cases are covered. If you have a case to add just report it.
