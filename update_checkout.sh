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

# If passed, set branch
BRANCH=$1

# Reset current working dir to prevent issues when switching branches
git reset --hard HEAD
git clean -f -d -q
# Go to desired branch and also reset that
git checkout ${BRANCH:"master"}
git reset --hard HEAD
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
