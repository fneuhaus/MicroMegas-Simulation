#!/bin/bash

if [ "$#" -ne 1 ]; then
        echo "Usage: $(basename $0) DIRECTORY"
        exit 1
fi

if [ ! -e "$1" ]; then
	echo "Directory $1 does not exist, creating..."
	mkdir "$1"
fi

WD="$(readlink -f $1)"

PHOTOCONVERSION_EXEC="/home/fneuhaus/micromegas-simulation/simulation/particleconversion/build/particleconversion"

echo "Using simulation directory: $WD"

# ROOT and Garfield++ setup
source /home/fneuhaus/micromegas-simulation/simulation/init.sh

cd $(dirname "$PHOTOCONVERSION_EXEC")
# needs about 300M ram for 100k photons
./$(basename "$PHOTOCONVERSION_EXEC") > $WD/particleconversion.log

STATUS=$?
exit $STATUS

