
[![Build Status](https://travis-ci.org/mapnik/python-mapnik.svg)](https://travis-ci.org/mapnik/python-mapnik)

Python bindings for Mapnik.

## Installation

Eventually we hope that many people will simply be able to `pip install mapnik` in order to get prebuilt binaries,
this currently does not work though. So for now here are the instructions

### Create a virtual environment

It is highly suggested that you [a python virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) when developing
on mapnik.

### Building from Mason

If you do not have mapnik built from source and simply wish to develop from the latest version in [mapnik master branch](https://github.com/mapnik/mapnik) you can setup your environment with a mason build. In order to trigger a mason build prior to building you must set the `MASON_BUILD` environment variable.

```bash
export MASON_BUILD=true
```

After this is done simply follow the directions as per a source build.

### Building from Source

Assuming that you built your own mapnik from source, and you have run `make install`. Set any compiler or linking environment variables as necessary so that your installation of mapnik is found. Next simply run one of the two methods:

```
python setup.py develop
```

If you wish to are currently developing on mapnik-python and wish to change the code in place and immediately have python changes reflected in your environment.

```
python setup.py install
```

If you wish to just install the package

## Testing

Once you have installed you can test the package by running:

```
python setup.py test
```

This might throw many errors if you have not included the [test data](https://github.com/mapnik/test-data) into your `tests/data` folder. If you want to do tests with out the extra data simply add `attr=!require_data` to the setup.cfg's `[nosetests]` section.


