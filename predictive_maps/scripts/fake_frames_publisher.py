#!/usr/bin/env python


import os
import yaml
from datetime import datetime

import roslib
import rospy

import tf

#from std_srvs.srv import Trigger
#from std_msgs.msg import String
#from std_msgs.msg import Int64
#from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
#from mongodb_store.message_store import MessageStoreProxy


class map_mux(object):

    def __init__(self) :
        self.listener1 = tf.TransformListener()
        self.br1 = tf.TransformBroadcaster()

        self.listener2 = tf.TransformListener()
        self.br2 = tf.TransformBroadcaster()
               
        self.transform_publisher=rospy.Timer(rospy.Duration(0.2),self.timer_callback, oneshot=False)        

        rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.scan_repub = rospy.Publisher('/fake_scan', LaserScan, latch=True, queue_size=1)
        
        rospy.spin()


    def timer_callback(self, blah):
        try:
            (trans,rot) = self.listener1.lookupTransform('base_link', 'base_laser_link', rospy.Time(0))
            self.br1.sendTransform(trans,rot,rospy.Time.now(),'fake_base_laser_link','fake_base_link')
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logwarn("tranform between base_link and base_laser_link not available")
        try:
            (trans,rot) = self.listener2.lookupTransform('odom', 'base_link', rospy.Time(0))
            self.br2.sendTransform(trans,rot,rospy.Time.now(),'fake_base_link','fake_odom')
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logwarn("tranform between odom and base_link not available")

    def scan_callback(self, msg):
        msg.header.frame_id='fake_base_laser_link'
        self.scan_repub.publish(msg)

        
    def _on_node_shutdown(self):
        #os.system('rosnode kill /slam_gmapping')
        self.transform_publisher.shutdown()
        print "BYE"

if __name__ == '__main__':
    rospy.init_node('fake_frames')
    server = map_mux()