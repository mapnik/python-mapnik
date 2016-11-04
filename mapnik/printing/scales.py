"""Scale helpers functions."""

import math


def any_scale(scale):
    """Scale helper function that allows any scale."""
    return scale

def sequence_scale(scale, scale_sequence):
    """Sequence scale helper, this rounds scale to a 'sensible' value."""
    factor = math.floor(math.log10(scale))
    norm = scale / (10**factor)

    for s in scale_sequence:
        if norm <= s:
            return s * 10**factor

    return scale_sequence[0] * 10**(factor + 1)

def default_scale(scale):
    """Default scale helper, this rounds scale to a 'sensible' value."""
    return sequence_scale(scale, (1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 6, 7.5, 8, 9, 10))

def deg_min_sec_scale(scale):
    for x in (1.0 / 3600,
              2.0 / 3600,
              5.0 / 3600,
              10.0 / 3600,
              30.0 / 3600,
              1.0 / 60,
              2.0 / 60,
              5.0 / 60,
              10.0 / 60,
              30.0 / 60,
              1,
              2,
              5,
              10,
              30,
              60
              ):
        if scale < x:
            return x
    else:
        return x
