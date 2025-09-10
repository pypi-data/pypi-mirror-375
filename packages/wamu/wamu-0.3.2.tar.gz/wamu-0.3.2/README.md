# wamu #

Pythom utilities for working with Weights and Measures.

## Precision ##

Wherever possible, `wamu` attempts to maintain the precision of a conversion as opposed
to relying on floating point math.  For example, converting from meters per second to
kilometers per hour would be calculated as:

    kmph = (mps * 3600.0) / 1000.0

However, the floating point division may result in loss of precision.  In such cases,
`wamu` will simplify the expression to:

    kmph = mps * 3.6
