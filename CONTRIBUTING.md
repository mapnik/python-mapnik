# Contributing

General guidelines for contributing to python-mapnik

## Coding Conventions

Much of python Mapnik is written in C++, and we try to follow general coding guidelines.

If you see bits of code around that do not follow these please don't hesitate to flag the issue or correct it yourself.

### C++ Style Guide

#### Prefix cmath functions with std::

The avoids ambiguity and potential bugs of using old C library math directly.

So always do `std::abs()` instead of `abs()`. Here is a script to fix your code in one fell swoop:


```sh
DIR=./bindings
for i in {abs,fabs,tan,sin,cos,floor,ceil,atan2,acos,asin}; do
    find $DIR -type f -name '*.cpp' -or -name '*.h' -or -name '*.hpp' | xargs perl -i -p -e "s/ $i\(/ std::$i\(/g;"
    find $DIR -type f -name '*.cpp' -or -name '*.h' -or -name '*.hpp' | xargs perl -i -p -e "s/\($i\(/\(std::$i\(/g;"
done
```

#### Avoid boost::lexical_cast

It's slow both to compile and at runtime.

#### Avoid sstream objects if possible

They should never be used in performance critical code because they trigger std::locale usage
which triggers locks

#### Spaces not tabs, and avoid trailing whitespace

#### Indentation is four spaces

#### Use C++ style casts

    static_cast<int>(value); // yes

    (int)value; // no


#### Use const keyword after the type

    std::string const& variable_name // preferred, for consistency

    const std::string & variable_name // no


#### Pass built-in types by value, all others by const&

    void my_function(int double val); // if int, char, double, etc pass by value

    void my_function(std::string const& val); // if std::string or user type, pass by const&

#### Use unique_ptr instead of new/delete

#### Use std::copy instead of memcpy

#### When to use shared_ptr and unique_ptr

Sparingly, always prefer passing objects as const& except where using share_ptr or unique_ptr express more clearly your intent. See http://herbsutter.com/2013/06/05/gotw-91-solution-smart-pointer-parameters/ for more details.

#### Shared pointers should be created with std::make_shared.

#### Use assignment operator for zero initialized numbers

    double num = 0; // please

    double num(0); // no


#### Function definitions should not be separated from their arguments:

    void foo(int a) // please

    void foo (int a) // no


#### Separate arguments by a single space:

    void foo(int a, float b) // please

    void foo(int a,float b) // no


#### Space between operators:

    if (a == b) // please

    if(a==b) // no


#### Braces should always be used:

    if (!file)
    {
        throw mapnik::datasource_exception("not found"); // please    
    }

    if (!file)
        throw mapnik::datasource_exception("not found"); // no


#### Braces should be on a separate line:

    if (a == b)
    {
        int z = 5;
        // more...
    }


#### Prefer `empty()` over `size() == 0` if container supports it

This avoids implicit conversions to bool and reduces compiler warnings.

    if (container.empty()) // please

    if (container.size() == 0) // no


### Other C++ style resources

Many also follow the useful [Google style guide](http://google-styleguide.googlecode.com/svn/trunk/cppguide.xml) which mostly fits our style. However, Google obviously has to maintain a lot of aging codebases. Mapnik can move faster, so we don't follow all of those style recommendations.

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

