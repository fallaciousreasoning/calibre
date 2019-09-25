# Calibre Converters
A fork of [calibre](https://github.com/kovidgoyal/calibre), intending to provide a (minimal) python library for running the calibre's ebook conversion tools.

A long term goal for this project is to run on the web, under [pyodide](https://github.com/iodide-project/pyodide/).

**NOTE:** This is very, very rough.

## Development

1. Clone the repository:
    ```
    git clone https://github.com/fallaciousreasoning/calibre.git
    ```
2. Run the bootstrap command (may require sudo):
    ```
    python setup.py bootstrap
    ```
3. Hopefully you can now convert ebooks!
   ```
   ./run-local ebook-convert path/to/input.epub path/to/ouput.mobi
   ```
4. Install missing packages with pip as needed...
    ```
    pip install <missing-package-1> ... <missing-package-n>
    ```

## calibre
This project is a fork of Calibre: https://github.com/kovidgoyal/calibre
<img align="left" src="resources/images/lt.png?raw=true" height="200" width="200"/>

calibre is an e-book manager. It can view, convert, edit and catalog e-books 
in all of the major e-book formats. It can also talk to e-book reader 
devices. It can go out to the internet and fetch metadata for your books. 
It can download newspapers and convert them into e-books for convenient 
reading. It is cross platform, running on Linux, Windows and macOS.