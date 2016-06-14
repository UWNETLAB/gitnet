#!/bin/bash
# A script for checking test coverage.
coverage run -a test_get.py
coverage run -a test_netgen.py
coverage run -a test_network.py
coverage run -a test_log.py
coverage run -a test_helpers.py
coverage report -m
coverage erase
