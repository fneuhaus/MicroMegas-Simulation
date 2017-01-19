#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Usage: $(basename $0) DIRECTORY"
	exit 1
fi

WD="$(readlink -f $1)"

INPUT_FILE="photoconversion.root"
AVAL_EXEC="/home/fneuhaus/micromegas-simulation/simulation/avalanche/avalanche"

echo "Using simulation directory: $WD"

if [ ! -e "$WD/$INPUT_FILE" ];
then
	echo "Input file: $INPUT_FILE does not exist!"
	exit 1
fi

# ROOT and Garfield++ setup
source /home/fneuhaus/micromegas-simulation/simulation/init.sh

# GNU Parallel
module load software/gnu_parallel

# run parallel on all split files
# needs about ?M RAM per job
find ${WD} -regextype posix-egrep -regex '^.*photoconversion_[0-9]+_drift\.root$' | parallel --colsep '_drift.root' -j 64 --delay 1 --progress --no-notice "$AVAL_EXEC {1}_drift.root {1}_aval.root > {1}_aval.log"

STATUS=$?
exit $STATUS

