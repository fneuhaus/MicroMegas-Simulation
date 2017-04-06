#!/bin/bash

project_path=$(dirname $0)
project_path=$(readlink -e $project_path)
export PYTHONPATH="${PYTHONPATH}:$project_path"

if [[ "$1" == "particleconversion" ]]; then
   echo "$1"
   echo "Building particleconversion..."
   cd "$project_path/particleconversion"
   mkdir -p "build" && cd "build"
   cmake -DCMAKE_INSTALL_PREFIX=.. ..
   make recog
   make
fi

echo "Building drift..."
cd "$project_path/drift"
make

echo "Building avalanche..."
cd "$project_path/avalanche"
make

echo "Done building..."
