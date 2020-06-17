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
git pull
git submodule init
git submodule update --recursive --remote
