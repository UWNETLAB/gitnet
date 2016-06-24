#!/bin/bash
# A script for generating html from the docstrings in our source files.
pdoc --html gitnet --overwrite
python gitnet/reparse.py
