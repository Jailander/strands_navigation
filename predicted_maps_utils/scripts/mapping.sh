#!/bin/bash

#mkdir Maps
#mkdir Done
#mkdir Fails
FILES=./*.bag
MAP_NAME="${PWD##*/}"

killall roscore
sleep 1
roscore &
sleep 1
rosparam set use_sim_time true
rosrun map_server map_server ../d.yaml &

echo "Starting gmapping"
rosrun gmapping slam_gmapping _maxUrange:=20.0 _xmin:=-100 _ymin:=-100 _xmax:=100 _ymax:=100 _delta:=0.05 _odom_frame:=map _map_frame:=gmap _minimumScore:=550.0 _srr:0.05 _srt:=0.05 _str:=0.05 _stt:=0.05 map:=gmap &
echo "done"


for f in $FILES
do
  echo "Processing $f file..."
  echo "done"

  rosbag play -r 1 "$f" map:=base_map_2
  #T=$?
done

timeout 100 rosrun map_server map_saver -f $MAP_NAME map:=gmap

S=$?
if [ "${S}" != "0" ]; then
  echo "Map Saver FAILED: ${S}" >> ./fails.txt
sleep 1
fi

#timeout 100 rosrun map_server map_saver -f $MAP_NAME_base map:=base_map

S=$?
if [ "${S}" != "0" ]; then
  echo "Base Map Saver FAILED: ${S}" >> ./fails.txt
sleep 1
fi

echo "done"
sleep 1
echo "Killing gmapping"
killall slam_gmapping
echo "done"
sleep 1
killall roscore

sleep 1
