# Required Dependencies
These are all the dependencies for calibre-converters.

> Note: Dependencies that are not pure python will need to be specially compiled to run on the web (or a have an alternative provided).

| Package         | Version   | Pure Python | Status                                                        |
| --------------- | --------- | ----------- | ------------------------------------------------------------- |
| lxml            | 4.4.0     | N           | Need                                                          |
| regex           | 2019.4.14 | N           | [Pyodide](https://github.com/iodide-project/pyodide/pull/538) |
| soupsieve       | 1.9.2     | Y           |
| css_parser      | 1.0.4     | Y           |
| html5lib        | 1.0.1     | Y           |
| html5_parser    | 0.4.8     | N           | Need                                                          |
| Image           | 1.5.27    | Y           |
| Pillow          | 6.1.0     | N           | Shim                                                          |
| PyQt5           | 5.13.1    | N           | Unneeded                                                      |
| beautifulsoup4  | 4.8.0     | Y           |
| python_dateutil | 2.8.0     | Y           |
| Markdown        | 3.1.1     | Y           |
| msgpack_python  | 0.5.6     | Y           |
| repr            | 0.3.1     | Y           |

## Explanation of statuses:
**Need:** Need in order to run. <br>
**Pyodide:** Need and supported in Pyodide <br>
**Shim:** Can be shimmed with web APIs. <br>
**Unneeded:** Not an actual requirement, should work without.