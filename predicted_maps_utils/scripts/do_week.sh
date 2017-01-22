#!/bin/bash

DIRS=./*/

for d in $DIRS
do
  echo "doing day $d"
  cd $d
    rosrun predicted_maps_utils extract_day_info.sh
  cd ..
done

sleep 1
