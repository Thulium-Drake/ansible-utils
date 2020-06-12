#!/bin/bash
# Retrieve the vault key
VAULT="$(basename $PWD).gpg"
VAULTDIR="$(dirname `readlink -f $0`)"
[ -f "$VAULTDIR/$VAULT" ] || exit 1
cat $VAULTDIR/$VAULT | gpg -qd
