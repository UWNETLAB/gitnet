#!/bin/bash
# A script for checking test coverage.
cd ..
coverage run -a gitnet_tests/test_network.py
coverage run -a gitnet_tests/test_netgen.py
coverage run -a gitnet_tests/test_get.py
coverage report -m
coverage erase
