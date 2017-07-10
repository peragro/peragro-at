#!/bin/bash

set -o errexit -o nounset

echo -e "Check for PR and branch.\n"

if [ "$TRAVIS_PULL_REQUEST" != "false" ]
then
  echo "This commit was made against pull request $TRAVIS_PULL_REQUEST! No deploy!"
  exit 0
fi

if [ "$TRAVIS_BRANCH" != "master" ]
then
  echo "This commit was made against the $TRAVIS_BRANCH and not the master! No deploy!"
  exit 0
fi

rev=$(git rev-parse --short HEAD)

echo -e "Starting to update gh-pages\n"

#generate and copy data we're interested in to other place
cd docs/
make html
echo "Copying html to " $HOME
cp -R _build/html $HOME/html_gen
echo "==============================="
ls -la $HOME/html_gen
echo "==============================="
ls -la .
echo "==============================="

git init
git config user.name "Travis"
git config user.email "travis@travis-ci.org"

git remote add upstream "https://$GH_TOKEN@github.com/peragro/peragro-at.git"
git fetch upstream
git reset upstream/gh-pages

touch .

git add -A .
git commit -m "rebuild pages at ${rev}"
git push -q upstream HEAD:gh-pages