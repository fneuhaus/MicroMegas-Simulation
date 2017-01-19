#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Usage: $(basename $0) DIRECTORY"
	exit 1
fi

WD="$1"

INPUT_FILE="particleconversion.root"
SPLIT_SCRIPT="/home/fneuhaus/micromegas-simulation/outfiles/scripts/splitFile.py"

echo "Using simulation directory: $WD"

if [ ! -e "$WD/$INPUT_FILE" ];
then
	echo "Input file: $INPUT_FILE does not exist!"
	exit 1
fi

# ROOT setup
source /home/fneuhaus/micromegas-simulation/simulation/init.sh

$SPLIT_SCRIPT -j 64 -t detectorTree $WD/$INPUT_FILE > $WD/split.log

STATUS=$?
exit $STATUS

