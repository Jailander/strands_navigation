#! /usr/bin/env python

import os
import sys
import rospy
#import rosnode
import yaml
from datetime import datetime
# Brings in the SimpleActionClient
import std_msgs #.msg import String

import cv2
import numpy as np


class pred_map_loader(object):
    
    def __init__(self) :
        self.endexec= False
        rospy.on_shutdown(self._on_node_shutdown)
       
#        while not self.endexec :
        sdate = datetime.now()
        print sdate.strftime("%Y-%m-%d %H:%M:%S")
        filename = sdate.strftime("%Y-%m-%d_%H-%M")
#        a,b=rosnode.kill_nodes['/slam_gmapping']
#        print a,b
        copycmdstr = 'rosrun map_server map_saver -f '+filename+' map:=gmap'
        print copycmdstr
        os.system(copycmdstr)
        os.system('rosnode kill /slam_gmapping')
        
    def _on_node_shutdown(self):
        self.endexec= True
        #sleep(2)


if __name__ == '__main__':
#    print 'Argument List:',str(sys.argv)
#    if len(sys.argv) < 2 :
#	sys.exit(2)
    rospy.init_node('pred_map_loader')
    ps = pred_map_loader()