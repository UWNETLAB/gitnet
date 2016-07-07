Name                                                                  Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------------------
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/__init__.py         6      0   100%
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/commit_log.py     113      3    97%   107-108, 163
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/exceptions.py      14      0   100%
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/get_log.py        103     14    86%   62, 111-118, 158, 160, 208-214, 242
test_commit_log.py                                                      259      0   100%
test_get.py                                                              92      1    99%   48
test_helpers.py                                                         201      0   100%
test_log.py                                                             678      0   100%
test_netgen.py                                                          111      0   100%
test_network.py                                                         524      0   100%
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/helpers.py        132      2    98%   55, 385
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/log.py            358      7    98%   199, 247-249, 251, 690, 707
/Users/jilliananderson/Documents/NetLab/gitnet/gitnet/multigraph.py     200      2    99%   150, 253
---------------------------------------------------------------------------------------------------
TOTAL                                                                  2791     29    99%

## 9 lines will not be run with our tests:
    - log.py            line 188,189,190,192
    - helpers.py        line 29 and 212
    - multigraph.py     line 98 or line 104
    - test_get.py       line 32
    - test_network.py   line 641 or line 643
