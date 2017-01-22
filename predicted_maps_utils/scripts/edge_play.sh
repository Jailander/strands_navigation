#!/bin/bash


FILES=./*.bag

#export ROS_MASTER_URI=http://alfred:11312
#roscore -p 11312 &

timeout 3 rostopic pub -l /initialpose geometry_msgs/PoseWithCovarianceStamped -f initial_pose.yaml

for f in $FILES
do
  echo "Processing $f file..."
 
  rosbag play "$f" amcl_pose:=amcl_pose_original
  T=$?
done

timeout 10 rosrun map_server map_saver -f base
timeout 10 rosrun map_server map_saver -f gmap map:=gmap

rosrun mapstitch mapstitch -o outmap.pgm base.pgm gmap.pgm
cp base.yaml outmap.yaml

sleep 1


