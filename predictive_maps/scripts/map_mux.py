#!/usr/bin/env python


#import os
#import yaml
#from datetime import datetime

#import roslib
import rospy

import tf

from std_srvs.srv import Trigger
from std_srvs.srv import Empty
#from std_msgs.msg import String
#from std_msgs.msg import Int64
from nav_msgs.msg import OccupancyGrid
#from mongodb_store.message_store import MessageStoreProxy


class map_mux(object):

    def __init__(self) :
        self.base_map_name=rospy.get_param('~base_map','/base_map')
        self.slam_map_name=rospy.get_param('~slam_map','/gmap')
        self.out_map_name=rospy.get_param('~out_map','/map')
        self.map_frame=rospy.get_param('~map_frame','map')
        self.amcl_frame=rospy.get_param('~amcl_frame','fake_odom')
        self.slam_frame=rospy.get_param('~slam_frame','slam')
        self.out_frame=rospy.get_param('~out_frame','odom')
        
        self.listener = tf.TransformListener()
        self.br = tf.TransformBroadcaster()
        
        self.map_index=1
        
        self.normal_map=False
        #self.first_time=True
        self.map_pub = rospy.Publisher(self.out_map_name, OccupancyGrid, latch=True, queue_size=1)
        
        rospy.Subscriber(self.base_map_name, OccupancyGrid, self.base_map_callback)
        rospy.Subscriber(self.slam_map_name, OccupancyGrid, self.slam_map_callback)
        
        self.switch_map_srv=rospy.Service('/switch_navigation_map', Trigger, self.switch_navigation_map_cb)
        
        self.transform_publisher=rospy.Timer(rospy.Duration(0.2),self.timer_callback, oneshot=False)        
        
        rospy.spin()

    def base_map_callback(self, msg):
        self.base_map = msg
        if self.map_index == 1:
            #print "got base map... republish"
            self.map_pub.publish(self.base_map)
            self.normal_map=True
        
    def slam_map_callback(self, msg):
        self.slam_map = msg
        if self.map_index == 2:
            #self.map_pub.publish(self.slam_map)
            self.normal_map=False


    def timer_callback(self, blah):
        #print "."
        try:
            if self.normal_map:
                (trans,rot) = self.listener.lookupTransform(self.map_frame, self.amcl_frame, rospy.Time(0))
            else:
                (trans,rot) = self.listener.lookupTransform(self.map_frame, self.slam_frame, rospy.Time(0))
            self.br.sendTransform(trans,rot,rospy.Time.now(),self.out_frame,self.map_frame)
            #print trans,rot
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            if self.normal_map:
                print "Can't find tranform between ", self.map_frame, " and ", self.amcl_frame
                                
            else:
                print "Can't find tranform between ", self.map_frame, " and ", self.slam_frame
        #self.br.sendTransform((0.0,0.0,0.0),(0.0,0.0,0.0,1.0),rospy.Time.now(),'odom','mux')
        


    def switch_navigation_map_cb(self, req):
        result, message = self.switch_navigation_map()
        try:
            rospy.wait_for_service('/move_base/clear_costmaps')
            clear_costmap = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
            clear_costmap()
        except rospy.ServiceException, e:
            rospy.logwarn("Service call failed: %s", e)
        return result, message
        
    def switch_navigation_map(self):
        if self.normal_map:
            self.map_index=2
            self.map_switch=rospy.get_param('/map_switch',False)
            if self.map_switch:
                self.map_pub.publish(self.slam_map)
            else:
                self.map_pub.publish(self.base_map)
            self.normal_map=False
            message='switched to slam map'
        else:
            self.map_index=1
            self.map_pub.publish(self.base_map)
            self.normal_map=True
            message='switched to base map'        
        return True, message


    def _on_node_shutdown(self):
        #os.system('rosnode kill /slam_gmapping')
        self.transform_publisher.shutdown()
        print "BYE"

if __name__ == '__main__':
    rospy.init_node('map_mux')
    server = map_mux()