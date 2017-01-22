#!/bin/bash


FILES=./*.bag

#export ROS_MASTER_URI=http://alfred:11312
#roscore -p 11312 &

timeout 3 rostopic pub -l /initialpose geometry_msgs/PoseWithCovarianceStamped -f initial_pose.yaml
rosbag record -o amcl_output /amcl_pose /particlecloud &

for f in $FILES
do
  echo "Processing $f file..."
 
  rosbag play "$f" -r $1 amcl_pose:=amcl_pose_original
  T=$?
done

killall rosbag

sleep 1


