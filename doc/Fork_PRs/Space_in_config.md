# Support space as separator in the Config field

- **Pull-request**: [#83](https://github.com/SchrodingersGat/KiBoM/pull/83)
- **Opened**: 2020-03-11
- **Status**: Merged (2020-03-12)

## Description

The config field name is configurable (`fit_field` option).
Its default separator is comma (**,**) which is useful for variants.
Other uses for this field are to mark a component as "Do Not Fit" (do not solder) and/or "Do Not Change" (must use the exact component).

This patch allows to mark **DNF** and **DNC** options using space as separator. Example:

```
DNF DNC +V1,-V2
```

Will mark the field as do not fit and do not change. It will also specify the variants information "+V1,-V2".

