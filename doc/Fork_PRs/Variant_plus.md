# Fixed variants with +VARIANT not working

- **Pull-request**: [#106](https://github.com/SchrodingersGat/KiBoM/pull/106)
- **Opened**: 2020-07-15
- **Status**: Open

## Description

The config field name is configurable (`fit_field` option).
One of its uses is to specify a list of variamts using comma (**,**) as separator.
Other uses for this field are to mark a component as "Do Not Fit" (do not solder) and "Do Not Change".

The variants mechanism was described by author in the [Kicad Forum](https://forum.kicad.info/t/flag-for-component-not-assembled-or-not-mounted-on-pcb/8169/2):

> Fitted or not fitted is a good start, but what you really want is assembly variants / configurations. Imagine some hypothetical board which you have to build for three customers, as well as have an in-house build with extra parts for debugging or test points or whatever.
> 
> Some part (let's call it U31) is fitted for Customers1, but not 2 or 3.
> 
> R17 is missing for Customer2 but loaded for all others.
> C99 is ONLY fitted for debug
> 
> See how it now becomes more complicated than just DNF?
> 
> So, you have the concept of a board configuration - there can be multiple configurations for a given board. In the schematic editor you can edit the configurations, add descriptions, etc. Then, each item in the schematic gets a "configuration" field, where you can specify which configurations correspond to each symbol.
> 
> e.g.
> 
> U31.configuration = -customer3
> R17.configuration = -customer2 -customer3
> C99.configuration = +debug
> 
> Where:
> 
> -xxx removes the part from configuration xxx
> +yyy specifies that the part is only fitted for configuration yyy
> You can chain multiple explicit configurations e.g. +xxx -yyy -zzz
> Unless defined otherwise given the points above, a part is assumed to be fitted.

So the idea is that components marked with *+VARIANT* are included **only** if you ask for *VARIANT*.
The initial implementation makes *+VARIANT* equivalent to nothing.

This problem was reported and a fix propposed in PR [#68](https://github.com/SchrodingersGat/KiBoM/pull/68).

This patch takes a different approach and removes various redundant operations.
