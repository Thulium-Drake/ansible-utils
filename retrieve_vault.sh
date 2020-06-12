#!/bin/bash
# Retrieve the vault key
VAULT="$(basename $PWD).gpg"
VAULTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cat $VAULTDIR/$VAULT | gpg -qd
