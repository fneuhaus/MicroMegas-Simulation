#!/bin/bash
set -o errexit
# set -o nounset

TARGET_DIR=$1
SIMULATION_CONF=$2
MESH_FILE=$3

cleanup() {
   # Disable trap
   trap - EXIT

   # Clean source
   $MICROMEGAS_SIMULATION_PATH/clear.sh

   # Restore default input files
   mv simulation.conf.orig simulation.conf
   mv avalanche/geometry/geometry.step.orig avalanche/geometry/geometry.step

   # Find the files to use
   if [[ "$SIMULATION_CONF" == "" ]] && [[ -f $TARGET_DIR/simulation.conf ]]; then
      SIMULATION_CONF=$TARGET_DIR/simulation.conf
   fi
   if [[ "$MESH_FILE" == "" ]] && [[ -f $TARGET_DIR/geometry/geometry.step ]]; then
      MESH_FILE=$TARGET_DIR/geometry/geometry.step
   fi
}

# Register cleanup
trap cleanup EXIT ERR INT TERM

# Backup default files and copy input files to correct location
cd $MICROMEGAS_SIMULATION_PATH
cp simulation.conf simulation.conf.orig
cp avalanche/geometry/geometry.step avalanche/geometry/geometry.step.orig
[[ -f "$SIMULATION_CONF" ]] && cp "$SIMULATION_CONF" simulation.conf || true
[[ -f "$MESH_FILE" ]] && cp "$MESH_FILE" avalanche/geometry/geometry.step || true

# Compile simulation
$MICROMEGAS_SIMULATION_PATH/build.sh > /tmp/micromegas_make.log 2>&1 || exit 1
echo "Compilation successfully completed."

# Copy binaries to target directory
cp particleconversion/build/particleconversion $TARGET_DIR/
cp particleconversion/*.mac $TARGET_DIR/
cp drift/drift $TARGET_DIR/
cp avalanche/avalanche $TARGET_DIR/
if [[ -d $TARGET_DIR/geometry ]]; then
   rm -R $TARGET_DIR/geometry
fi
cp -r avalanche/geometry/ $TARGET_DIR/

# Copy simulation configuration
cp simulation.conf $TARGET_DIR/
echo "Copied binaries."
