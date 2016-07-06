#!/bin/bash
# A script for generating html from the docstrings in our source files.
pdoc --html gitnet --overwrite
python gitnet/reparse.py
# python gitnet/reparse.py
# To use a mako theme, add the command --template-dir theme after the 'pdoc' command, and comment out the python 'gitnet/reparse.py' line.
# To use the parser make sure that the directory is pointing to the 'reparse.py' file, and remove the --template-dir command if there is one.
