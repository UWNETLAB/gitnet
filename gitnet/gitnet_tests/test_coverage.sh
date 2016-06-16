#!/bin/bash
# A script for checking test coverage.
coverage run -a test_get.py
coverage run -a test_netgen.py
coverage run -a test_network.py
coverage run -a test_log.py
coverage run -a test_helpers.py
coverage report -m
coverage report -m > coverage_report.md
coverage erase

echo "
## 5 lines will not be run with our tests:
    - helpers.py        line 29 and 212
    - multigraph.py     line 98 or line 104
    - test_get.py       line 32
    - test_network.py   line 641 or line 643" >> coverage_report.md
