#!/usr/bin/env bash
git init
touch base.md
echo "Hello there." >> base.md
git add base.md
git commit -m "created the base file." --author="Randy <randy@gmail.com>" --date="Fri May 20 9:19:20 2016 -0400"

git checkout -b newbranch
echo "See you later." >> base.md
git add base.md
git commit -m "edited base on new branch." --author="Annie <annie@gmail.com>" --date="Fri May 20 9:30:45 2016 -0400"

git checkout master
git merge -d newbranch

# Replace old repo (inactive)
FNAME="branch_merge_repo"
rm -rf $FNAME.git
cp -R .git $FNAME.git
rm -rf .git

# the repos created by this script and the blank_message script should be identical except for the messages.
