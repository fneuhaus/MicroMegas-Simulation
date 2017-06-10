#!/bin/bash
FOLDER="$1"
STEP="$2"

shopt -s nullglob
cd $FOLDER
for FILE in *_${STEP}.log; do
   JOB_NUM=`basename "$FILE" "_${STEP}.log"`
   if [ "$STEP" == "drift" ]; then
      PROGRESS=`tac $FILE | grep -o -m 1 -e "[0-9]*[\.0-9]*%" -e "Done."`
      PROGRESS="${PROGRESS//$'\r'/$''}"
   fi
   if [ "$STEP" == "avalanche" ]; then
      PROGRESS=`tac $FILE | grep -o -m 1 -e "Done." -e "^[0-9]*[\.0-9]*% of all events"`
      PROGRESS="${PROGRESS//$' of all events'/$''}"
   fi
   STATUS=$?
   if [ "$STATUS" != "0" ] || [ "$PROGRESS" == "" ]; then
      PROGRESS="n/a"
   fi
   echo "${JOB_NUM}:${PROGRESS}"
done
