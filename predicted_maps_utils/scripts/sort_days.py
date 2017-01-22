#!/usr/bin/env python

import sys
import yaml
import glob
import os

#import datetime
#import std_msgs.msg
#from geometry_msgs.msg import Pose
#from std_msgs.msg import String
#from rosgraph_msgs.msg import Clock


class sort_days(object):

    def __init__(self, prefix) :
        self.create_folders(prefix)

    
    def create_folders(self, prefix):
        for i in range(1,32):
            day_name="%02d" %i
            folder_name=prefix+'-'+day_name
            print 'Creating folder: '+folder_name
            try:
                os.stat(folder_name)
            except:
                os.mkdir(folder_name)           
            cmd = 'mv '+folder_name+'-* '+folder_name
            print cmd
            os.system(cmd)

if __name__ == '__main__':
    print 'Argument List:',str(sys.argv)
    if len(sys.argv) < 2 :
	sys.exit(2)
    server = sort_days(sys.argv[1])