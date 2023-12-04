# OCPARSE 

Module for parsing and analyzing machine code instructions

The module provides a class Parser for a machine code parsers and a corresponding class Opcode for opcode-patterns that defines bitpatterns and/or bitfields of which the parser can extract the values. It also has an analyzer class Analyzer with its own opocde class AnalyzerOpcode that can be used for analysis of instruction sets and their decoding.

## Installation 
Copy the file ocparse.py to a location where it is found by Python. The code is tested with Python 3.10.

## Documentation 
The documentation in the docs-directory and is based on [Sphinx](https://www.sphinx-doc.org/en/master/#). Type simply `make` for a list of possible formats. The formats `html`, `latexpdf` and `man` have been tested.

## Examples 
Some examples of use are found in the correspondingly named folder.
