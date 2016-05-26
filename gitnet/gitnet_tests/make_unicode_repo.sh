git init
touch README.md
echo 'Hełło, this is a 読んでね. наслаждаться.'
git add README.md
git commit -m "Readme created. شديد الرطوبة. Contains: Hełło, this is a 読んでね. наслаждаться." --author="Arngärdh <arngaardh@gmail.com>" --date="Fri May 20 9:19:20 2016 -0400"

FNAME="unicode_repo"
rm -rf $FNAME.git
cp -R .git $FNAME.git
rm -rf .git
