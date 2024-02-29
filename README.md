
[![Build Status](https://travis-ci.org/mapnik/python-mapnik.svg)](https://travis-ci.org/mapnik/python-mapnik)

Python bindings for Mapnik.

## Installation

Eventually we hope that many people will simply be able to `pip install mapnik` in order to get prebuilt binaries,
this currently does not work though. So for now here are the instructions

### Create a virtual environment

It is highly suggested that you have [a python virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) when developing
on mapnik.

### Building from Mason

If you do not have mapnik built from source and simply wish to develop from the latest version in [mapnik master branch](https://github.com/mapnik/mapnik) you can setup your environment with a mason build. In order to trigger a mason build prior to building you must set the `MASON_BUILD` environment variable.

```bash
export MASON_BUILD=true
```

After this is done simply follow the directions as per a source build.

### Building from Source

For detailed MacOS with Homebrew instructions, see section below

Assuming that you built your own mapnik from source, and you have run `make install`. Set any compiler or linking environment variables as necessary so that your installation of mapnik is found. Next simply run one of the two methods:

```
python setup.py develop
```

If you are currently developing on mapnik-python and wish to change the code in place and immediately have python changes reflected in your environment.


```
python setup.py install
```

If you wish to just install the package.

```
python setup.py develop --uninstall
```

Will de-activate the development install by removing the `python-mapnik` entry from `site-packages/easy-install.pth`.


If you need Pycairo, make sure that PYCAIRO is set to true in your environment or run:

```
PYCAIRO=true python setup.py develop
```

### Building on MacOS Catalina with Homebrew: use mapnik/master and python-mapnik-master

On MacOS Catalina with Homebrew, the homebrew's mapnik version (3.0) conflicts with the boost version (>1.73). 

Its much easier to compile mapnik 4.0 from `mapnik/master`, and compile `python-mapnik` against that.

#### First: setup homebrew packages

```
# note: boost needs to be >= 1.73, make sure boost@1.73 is linked too
brew install boost boost-python3 sqlite gdal cairo python@3.8
brew upgrade boost boost-python3 sqlite gdal cairo python@3.8
brew link boost

# We're build a custom mapnik 4, uninstall the stale 3.x version in homebrew:
brew uninstall mapnik
```

#### Second: build `mapnik/master`

Setting the `PYTHON=python2` env var is important, an older fork of SConstruct is embedded in mapnik source, which will not work with `python` if its linked to `python3` as on some MacOS systems. Passing a path to sqlite3 will select the homebrew version instead of the MacOS system version (which doesn't include support for sqlite extensions and will break the mapnik compile).

```
brew install boost 
git clone https://github.com/mapnik/mapnik ; cd mapnik
git submodule update --init
PYTHON=python2 ./configure. SQLITE_INCLUDES=/usr/local/opt/sqlite3/include
make
make install
```

#### Finally: build `python-mapnik/master`

Homebrew includes the python version in the libboost_python38.dylib name, which is not autodetected, and must be explicitly referenced:

```
git clone https://github.com/mapnik/python-mapnik ; cd python-mapnik
BOOST_PYTHON=boost_python38 python3 setup.py install
```

### Building against Mapnik 3.0.x

The `master` branch is no longer compatible with `3.0.x` series of Mapnik. To build against Mapnik 3.0.x, use [`v3.0.x`](https://github.com/mapnik/python-mapnik/tree/v3.0.x) branch.

## Testing

Once you have installed you can test the package by running:

```
git submodule update --init
python setup.py test
```

The test data in `./test/data` and `./test/data-visual` are standalone modules. If you need to update them see https://github.com/mapnik/mapnik/blob/master/docs/contributing.md#testing


### Troubleshooting

If you hit an error like:

```
Fatal Python error: PyThreadState_Get: no current thread
Abort trap: 6
```

That means you likely have built python-mapnik linked against a different python version than what you are running. To solve this try running:

```
/usr/bin/python <your script.py>
```

If you hit an error like the following when building with mason:

```
EnvironmentError: 
Missing boost_python boost library, try to add its name with BOOST_PYTHON_LIB environment var.
```

Try to set `export BOOST_PYTHON_LIB=boost_python` before build.
Also, if `boost_thread` or `boost_system` is missing, do likewise:

```
export BOOST_SYSTEM_LIB=boost_system
export BOOST_THREAD_LIB=boost_thread
```

If you still hit a problem create an issue and we'll try to help.

## Tutorials

- [Getting started with Python bindings](docs/getting-started.md)
