#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:06:35 2015

@author: cdondrup & Jailander
"""

import os
import yaml
import rospy
import actionlib
from random import shuffle
from topological_navigation.msg import GotoNodeAction, GotoNodeGoal
from strands_navigation_msgs.msg import TopologicalMap
from strands_navigation_msgs.srv import PauseResumeNav
from geometry_msgs.msg import PoseStamped, Pose
from mongodb_store.message_store import MessageStoreProxy
from strands_gazing.msg import GazeAtPoseAction, GazeAtPoseGoal
from flir_pantilt_d46.msg import PtuGotoAction, PtuGotoGoal
from std_msgs.msg import String
from std_msgs.msg import Int64
from nav_msgs.msg import OccupancyGrid
import tf


def load_wp_yaml(filename):
    print "loading: ",filename
    with open(filename, 'r') as f:
        return yaml.load(f)

class TopPatroller(object):
    node_names = []
    robot_pose = Pose()
    card_pose = Pose()

    def __init__(self, name):
        self.stop=False
        self.first_charge=True
        rospy.on_shutdown(self._on_node_shutdown)
        rospy.loginfo("starting %s ..." % name)
        self.msg_store = MessageStoreProxy(collection="card_interactions")
        self.listener = tf.TransformListener()
        self.wait_time = rospy.get_param("~wait_at_node", 30.)
        rospy.loginfo("Creating and waiting for ptu server")
        self.ptu_client = actionlib.SimpleActionClient("SetPTUState", PtuGotoAction)
        self.ptu_client.wait_for_server()
        rospy.loginfo("Creating and waiting for gaze server")
        self.gaze_client = actionlib.SimpleActionClient("gaze_at_pose", GazeAtPoseAction)
        self.gaze_client.wait_for_server()
        rospy.loginfo("... done")
        rospy.Subscriber('topological_map', TopologicalMap, self.map_callback)
        rospy.Subscriber('/socialCardReader/commands', String, self.card_callback, queue_size=1)
        rospy.Subscriber('/robot_pose', Pose, self.robot_callback)
        rospy.Subscriber('/socialCardReader/cardposition', PoseStamped, self.card_pose_callback)
        
        # Predictive Mapping        
        self.map_name_pub = rospy.Publisher('/mapName', String, latch=True, queue_size=1)
        self.map_time_pub = rospy.Publisher('/addTime', Int64, latch=True, queue_size=1)
        self.map_save_pub = rospy.Publisher('/route_map', OccupancyGrid, latch=True, queue_size=1)

        self.pred_time_pub = rospy.Publisher('/predictTime', Int64, latch=True, queue_size=1)
        self.pred_ord_pub = rospy.Publisher('/predictOrder', Int64, latch=True, queue_size=1)
        rospy.Subscriber('/current_node', String, self.current_node_callback)
        
        self.route = load_wp_yaml('./route.yaml')
        print "---Map Route--"
        print self.route
        print "---Map Route--"
        self.waypoints = self.get_nodes()
        shuffle(self.waypoints)
        print self.waypoints
        self.client = actionlib.SimpleActionClient('topological_navigation', GotoNodeAction)
        self.client.wait_for_server()
        rospy.loginfo("all done ...")
        self.node_loop()

    def _transform(self, msg, target_frame):
        if msg.header.frame_id != target_frame:
            try:
                t = self.listener.getLatestCommonTime(target_frame, msg.header.frame_id)
                msg.header.stamp = t
                return self.listener.transformPose(target_frame, msg)
            except (tf.Exception, tf.LookupException, tf.ConnectivityException) as ex:
                rospy.logwarn(ex)
                return None
        else:
            return msg

    def node_loop(self):
        #cnt = 0
        while not self.stop:#rospy.is_shutdown():
            for i in self.route:
                if self.stop:
                    break
                rospy.loginfo("Going to: [%s]" % i)
                print i
                ng = GotoNodeGoal()
                ng.target = i
                ng.no_orientation = False
                self.client.send_goal(ng)
                self.client.wait_for_result()
                ps = self.client.get_result() 
                print "Result: ", ps
                g = GazeAtPoseGoal()
                g.topic_name = "/upper_body_detector/closest_bounding_box_centre"
                self.gaze_client.send_goal(g)
                g = PtuGotoGoal()
                g.pan = 0.0
                g.tilt = 30.0
                g.pan_vel = 60.
                g.tilt_vel = 60.
                self.ptu_client.send_goal(g)
                rospy.sleep(self.wait_time)

            shuffle(self.waypoints)
            for i in self.waypoints:
                if self.stop:
                    break
                rospy.loginfo("Going to: [%s]" % i)
                print i
                ng = GotoNodeGoal()
                ng.target = i
                ng.no_orientation = False
                self.client.send_goal(ng)
                self.client.wait_for_result()
                ps = self.client.get_result() 
                print "Result: ", ps
                g = GazeAtPoseGoal()
                g.topic_name = "/upper_body_detector/closest_bounding_box_centre"
                self.gaze_client.send_goal(g)
                g = PtuGotoGoal()
                g.pan = 0.0
                g.tilt = 30.0
                g.pan_vel = 60.
                g.tilt_vel = 60.
                self.ptu_client.send_goal(g)
                rospy.sleep(self.wait_time)


    def current_node_callback(self, msg):
        print "current node: ", msg
        if msg.data == 'ChargingPoint' and not self.first_charge:
            self.save_pred_map()
        else:
            if msg.data != 'ChargingPoint':
                self.first_charge = False
    
    def save_pred_map(self):
        try:
            self.timestamp = int(rospy.get_time())
            print "Getting map for: ", self.timestamp
            self.route_map = rospy.wait_for_message('/gmap',OccupancyGrid, timeout=10)
            self.map_name = rospy.get_param('topological_map_name', 'world')
            print "got map: ",self.map_name
            self.upload_map()
            rospy.sleep(2.0)
            self.predict_map()
            copycmdstr = 'rosrun map_server map_saver -f ~/predicted_maps/'+str(self.timestamp)+' map:=gmap'
            print copycmdstr
            os.system(copycmdstr)
            os.system('rosnode kill /slam_gmapping')
        except:
            print "no map received"


    def upload_map(self):
        self.map_name_pub.publish(self.map_name)
        self.map_time_pub.publish(self.timestamp)
        self.map_save_pub.publish(self.route_map)

    def predict_map(self):
        print "Requesting Prediction"
        self.pred_ord_pub.publish(0)
        time = int(rospy.get_time()) + int(self.wait_time)
        print "Requesting Prediction for time: ", time
        self.pred_time_pub.publish(time)            

    def map_callback(self, msg):
        print 'got map: %s' % len(msg.nodes)
        self.node_names = [node.name for node in msg.nodes if not node.name.startswith('Ramp')]
        self.node_names.pop(self.node_names.index('ChargingPoint'))

    def get_nodes(self):
        while not rospy.is_shutdown() and len(self.node_names) == 0:
            print 'no nodes'
            rospy.sleep(1)
        return self.node_names

    def robot_callback(self, msg):
        self.robot_pose = msg

    def card_pose_callback(self, msg):
        self.card_pose = msg

    def card_callback(self, msg):
        rospy.loginfo("Found card: %s" % msg.data)
        if msg.data == "INFO_TERMINAL":
            rospy.loginfo("Saving positions")
            meta = {}
            meta["entity"] = "card"
            pose = self._transform(self.card_pose, "/map")
            if pose != None:
                self.msg_store.insert(pose, meta)
                meta["entity"] = "robot"
                robot_pose = PoseStamped(header=pose.header, pose=self.robot_pose)
                self.msg_store.insert(robot_pose, meta)
            else:
                rospy.logwarn("Transformation failed. Trying to save original data")
                self.msg_store.insert(self.card_pose, meta)
                meta["entity"] = "robot"
                robot_pose = PoseStamped(header=self.card_pose.header, pose=self.robot_pose)
                self.msg_store.insert(robot_pose, meta)
            try:
                rospy.loginfo("Creating and waiting for pause service")
                r = rospy.ServiceProxy("/monitored_navigation/pause_nav", PauseResumeNav)
                r.wait_for_service(timeout=1.)
                rospy.loginfo("PAUSE")
                r(pause=True)
                rospy.sleep(10.)
                rospy.loginfo("RESUME")
                r(pause=False)
            except:
                pass

    def _on_node_shutdown(self):
        print "BYE"
        self.stop = True


if __name__=="__main__":
    rospy.init_node("top_patroller")
    t = TopPatroller(rospy.get_name())
    rospy.spin()
