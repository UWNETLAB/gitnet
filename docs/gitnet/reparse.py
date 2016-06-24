# Python sccript for adding images to the html files in a reproducible way.
import os
import subprocess as subprocess
import sys
import glob
import fileinput

find = '<h1>Index</h1>'
replace = '<img src="static/gitnet.png" height="250" width="250"/>'

files = glob.glob('gitnet/*.m.html')
for file in files:
    with fileinput.FileInput(file, inplace=True) as html_file:
        for line in html_file:
            print(line.replace(find, replace), end='')
