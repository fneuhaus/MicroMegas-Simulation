#!/bin/bash

if [ "$#" -lt 2 ]; then
	echo "Usage: $(basename $0) DEST_FILE SOURCE_FILE [SOURCE_FILE]"
	exit 1
fi

# ROOT and Garfield++ setup
source /home/fneuhaus/micromegas-simulation/simulation/init.sh

$ROOTSYS/bin/hadd -f $@

STATUS=$?
exit $STATUS

