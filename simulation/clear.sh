#!/bin/bash

curPath=$PWD
project_path=$(readlink -e $(dirname $0))
echo $project_path

cd $project_path/particleconversion/build/
make clean-cog

cd $project_path/avalanche/
make clean-cog

cd $project_path/drift/
make clean-cog

cd $curPath
