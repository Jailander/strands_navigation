#!/usr/bin/env python

#import sys
import yaml
import glob
import os

#import datetime
#import std_msgs.msg
#from geometry_msgs.msg import Pose
#from std_msgs.msg import String
#from rosgraph_msgs.msg import Clock


class filter_bags(object):

    def __init__(self) :
        self.load_bag_info()
        self.create_route_folders()
        #self.create_edge_folders()

    def load_bag_info(self):
        with open('day_info.yml', 'r') as f:
            self.info = yaml.load(f)
            print self.info['routes']
    
    def create_route_folders(self):
        cwd = os.getcwd().rsplit('/',1)
        cwd = cwd[1]
        print cwd
        for i in self.info['routes']:
            if i['duration'] > 180:
                folder_name = i['date']
                print 'Creating folder: '+folder_name
                try:
                    os.stat(folder_name)
                except:
                    os.mkdir(folder_name)
                print 'Filtering bags'
                for j in i['bags']:
                    bagname = j.lstrip('./')
                    bagname = bagname.rstrip('.bag')
                    cmd = 'rosbag filter '+ j +' '+folder_name+'/'+bagname+'_filtered.bag'+' \"t.to_sec() >= '+str(i['started'])+'.00 and t.to_sec() <= '+str(i['finished'])+'.00\"'
                    print cmd
                    os.system(cmd)
            else:
                print "Tour too short discarding..."

    def create_edge_folders(self):
        cwd = os.getcwd().rsplit('/',1)
        cwd = cwd[1]
        print cwd
        for i in self.info['edges_traversed']:
            if i['duration'] > 3:
                folder_name = i['name']
                print 'Creating folder: '+folder_name
                try:
                    os.stat(folder_name)
                except:
                    os.mkdir(folder_name)
                print 'Filtering bags'
                for j in i['bags']:
                    bagname = j.lstrip('./')
                    bagname = bagname.rstrip('.bag')
                    stime=str(i['start_time']-10)
                    etime=str(i['end_time']+10)
                    cmd = 'rosbag filter '+ j +' '+folder_name+'/'+bagname+'_filtered.bag'+' \"t.to_sec() >= '+stime+'.00 and t.to_sec() <= '+etime+'.00\"'
                    print cmd
                    os.system(cmd)
            else:
                print "Edge too short discarding..."

if __name__ == '__main__':
    server = filter_bags()