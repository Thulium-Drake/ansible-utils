#!/bin/bash
# DO NOT MOVE THIS SCRIPT!
#
# This script will update the current git checkout and it's submodules
#
# It will not remove files/directories put in .gitignore
#
# Run in cron for the best results
GITREPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# As this script is in the scripts folder and we need to run the commands below
# in the Git root
cd $GITREPO/..

# If passed, set branch and origin
INPUT=$1
ORIGIN=${INPUT%%/*}
BRANCH=${INPUT##*/}

# If there's no origin in the input, assume defaults
if [ "$ORIGIN" == "$BRANCH" ]
then
  unset ORIGIN
fi

# Reset current working dir to prevent issues when switching branches
CUR_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/')
git reset --hard ${ORIGIN:"origin"}/$CUR_BRANCH
git clean -f -d -q
# Go to desired branch and also reset that
git checkout ${BRANCH:"master"}
git reset --hard ${ORIGIN:"origin"}/${BRANCH:"master"}
git clean -f -d -q

# Update code
git pull
git submodule update
git submodule update --init --recursive
git submodule foreach git reset --hard HEAD
git submodule foreach git clean -f -d -q -x
git submodule foreach git submodule update --init --recursive
git submodule foreach git fetch
git submodule foreach git pull
