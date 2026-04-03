Python bindings for [Mapnik](https://mapnik.org) [v4.2.2](https://github.com/mapnik/python-mapnik/releases/tag/v4.2.2)

| Platform/Interpreter | cp39     | cp310 | cp311 | cp312 | cp313 | cp314 |
|----------|----------|-------|-------|-------|-------|-------|
| macosx_11_0_arm64 | ✅ | ✅  | ✅   | ✅   | ✅   | ✅ |  ✅ | ✅ |
| macosx_11_0_x86_64|  ✅ | ✅  | ✅   | ✅   | ✅   | ✅ |  ✅ | ✅ |
| manylinux_2_31_arm64 | ✅ | ✅  | ✅   | ✅   | ✅   | ✅ |  ✅ | ✅ |
| manylinux_2_31_x86_64 |  ✅ | ✅  | ✅   | ✅   | ✅   | ✅ |  ✅ | ✅ |

## Installation

```
python3 -m pip install mapnik
```

### Building from Source

Make sure 'mapnik-config' is present and accessible via $PATH env variable 

```
python3 -m pip install . -v 
```

## Testing

Once you have installed you can test the package by running:

```
pytest test/python_tests/
```




