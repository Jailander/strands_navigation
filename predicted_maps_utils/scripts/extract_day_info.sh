#!/bin/bash


FILES=./*.bag
DIRS=./*/

#rosbag compress *.bag


for h in $FILES
do
  echo "extracting info for $h ..."
  rosbag info -y "$h" >> "$h".yaml
done

killall roscore
sleep 1
roscore &
sleep 1
rosparam set /use_sim_time true
sleep 1
rosrun predicted_maps_utils bag_reader.py &
sleep 1

for f in $FILES
do
  echo "Processing $f file..."
  rosbag play "$f" --clock -r 100 -q
done

rosnode kill /extract_info
killall roscore
rm ./*.bag.yaml

#mkdir routes
#mkdir edges
rosrun predicted_maps_utils create_routes.py

sleep 3

rosrun predicted_maps_utils do_mapping.sh

DIR_NAME=${PWD##*/}

cp day_info.yml ../$DIR_NAME.yml

sleep 1


