# Added "join" to join fields like voltage, current, etc. with the value

- **Pull-request**: [#81](https://github.com/SchrodingersGat/KiBoM/pull/81)
- **Opened**: 2020-03-11
- **Status**: Open

## Description

1 nF 50 V isn't the same as 1 nF 100 V and having separated columns for each possible modifier is an overkill. Joining the fields to the value is compact and natural.

## How to use

Define a section named `[JOIN]`. In this section each entry is the name of a field, followed by the name of the fields that will be added to its column.
Use tab (ASCII 9) as separator. Example:

```
[JOIN]
value	voltage	current	power	tolerance
```

This will attach the `voltage`, `current`, `power` and `tolerance` fields to the `value` field.

