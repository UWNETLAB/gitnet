#!/usr/bin/env bash
git init

# Replace old repo (inactive)
FNAME="repo_zero"
rm -rf $FNAME.git
cp -R .git $FNAME.git
rm -rf .git
