#!/usr/bin/env bash
git init
touch readme.md
echo "This is a readme." >> readme.md
git add readme.md
git commit -m "Made readme." --author="Alice <alice@gmail.com>" --date="Fri May 6 14:41:25 2016 -0400"
echo "Added new features." >> readme.md
git add readme.md
git commit -m "Edited readme." --author="Bob <bob@gmail.com>" --date="Fri May 6 14:50:22 2016 -0400"
git log >> "basic_logs.txt"
git log --raw >> "raw_logs.txt"
git log --stat >> "stat_logs.txt"
git add basic_logs.txt
git add raw_logs.txt
git add stat_logs.txt
git commit -m "Recorded logs." --author="Alice <alice@gmail.com>" --date="Fri May 6 15:41:25 2016 -0400"

# Replace old repo (inactive)
FNAME="repo_one"
rm -rf $FNAME.git
cp -R .git $FNAME.git
rm -rf .git
