#!/bin/bash
# DO NOT MOVE THIS SCRIPT!
#
# This script will update the current git checkout and it's submodules
#
# Run in cron for the best results
GITREPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# As this script is in the scripts folder and we need to run the commands below
# in the Git root
cd $GITREPO/..

# Reset entire repo and update
git reset --hard HEAD
git clean -f -d -q
git checkout master
git fetch origin master
git reset --hard origin/master
git pull
git submodule update
git submodule update --init --recursive
git submodule foreach git reset --hard HEAD
git submodule foreach git clean -f -d -q -x
git submodule foreach git submodule update --init --recursive
git submodule foreach git fetch
git submodule foreach git pull
