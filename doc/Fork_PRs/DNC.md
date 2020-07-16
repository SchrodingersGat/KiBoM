# Added support for "DNC" or "do not change" in Config

- **Pull-request**: [#84](https://github.com/SchrodingersGat/KiBoM/pull/84)
- **Opened**: 2020-03-11
- **Status**:
  - Closed by [#91](https://github.com/SchrodingersGat/KiBoM/pull/91) (2020-03-12). Same idea, but better implementation by upstream.
  - Fixed by [Fix DNC (isFixed) #105](https://github.com/SchrodingersGat/KiBoM/pull/105) (2020-07-15)

## Description

Used for components that shouldn't be replaced for a simple equivalent, needs approval.

The config field name is configurable (`fit_field` option).
Its default separator is comma (**,**) which is useful for variants.
Other uses for this field are to mark a component as "Do Not Fit" (do not solder).
This patch also adds the ability to mark it as "Do Not Change".

Valid values to mark it are:
- DNC
- Do Not Change
- No Change
- Fixed

The parser is case insensitive. You can use *DNC*, or *dnc*, or *Dnc*, etc.

DNC components indicates **(DNC)** in the *Quantity Per PCB* column.

## How to use

Add the *DNC* word to the `Config` field.
