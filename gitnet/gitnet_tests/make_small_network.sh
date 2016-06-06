#!/usr/bin/env bash
git init

touch file1.md
echo "Author 1" >> file1.md
touch file2.md
echo "Author 1" >> file2.md
touch file3.md
echo "Author 1" >> file3.md
touch file4.md
echo "Author 1" >> file4.md
git add file1.md file2.md file3.md file4.md
git commit -m "created 4 files." --author="Randy <randy@gmail.com>" --date="Fri May 20 9:19:20 2016 -0400"

echo "Author 2" >> file3.md
touch file5.md
echo "Author 2" >> file5.md
git add file3.md file5.md
git commit -m "created 1 file, added to file 3." --author="Jenna <jenna@gmail.com>" --date="Mon May 23 2:45:25 2016 -0400"

echo "Author 3" >> file4.md
echo "Author 3" >> file5.md
touch file6.md
echo "Author 3" >> file6.md
git add file4.md file5.md file6.md
git commit -m "created 1 file, added to file 4 and file 5." --author="Billy G <bill@gmail.com>" --date="Wed May 25 1:12:48 2016 -0400"

echo "Author 4" >> file6.md
touch file7.md
echo "Author 4" >> file7.md
git add file6.md file7.md
git commit -m "created 1 file, added to file 3." --author="Marcela <marcy@gmail.com>" --date="Thu May 26 11:21:03 2016 -0400"

# Replace old repo (inactive)
FNAME="small_network_repo"
rm -rf $FNAME.git
cp -R .git $FNAME.git
rm -rf .git

# should follow the pattern: 4 authors, 4 commits, 7 files.
# Density: 0.39
# Average Degree: ???
# 11 Nodes, 11 Edges
