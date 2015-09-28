# Contributing

General guidelines for contributing to python-mapnik

## Coding Conventions

See the [Mapnik guide](https://github.com/mapnik/mapnik/blob/master/docs/contributing.md#coding-conventions).

### Python Style Guide

All python code should follow PEP8 as closely as possible. However, we do not strictly enforce all PEP8 such as 80 characters per line.

## Testing

In order for any code to be pulled into master it must contain tests for **100%** of all lines. The only lines that are not required to be tested are those that cover extreme cases which can not be tested with regularity, such as race conditions. 

If this case does occur you can put a comment block such as shown below to exclude the lines from test coverage.

```C++
// LCOV_EXCL_START
can_not_reach_code();
// LCOV_EXCL_END
```

## Releasing

To release a new python-mapnik version:

Currently just hit up @flippmoke, this section will be filled out ASAP!

### Documentation

TODO: Write documentation on how to update documentation.

