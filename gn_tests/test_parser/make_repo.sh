#!/usr/bin/env bash
git init
touch readme.md
echo "This is a readme." >> readme.md
git add readme.md
git commit -m "Made readme." --author="Alice <alice@gmail.com>" --date="Fri May 6 14:41:25 2016 -0400"
echo "Added new features." >> readme.md
git add readme.md
git commit -m "Made readme." --author="Bob <bob@gmail.com>" --date="Fri May 6 14:50:22 2016 -0400"
git log >> "test_logs.txt"
