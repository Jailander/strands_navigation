#!/usr/bin/env python

#import sys
import yaml
import rospy
import glob

import datetime
#import std_msgs.msg
#from geometry_msgs.msg import Pose
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock


class infoExtract(object):

    def __init__(self) :
        self.nnodes_visited=0
        self.times_at_charging=0
        self.bag_data={}
        self.bag_data['nodes_visited']=[]
        self.bag_data['routes']=[]
        self.bag_data['bag_info']=[]
        self.bag_data['edges_traversed']=[]
        self.prev_node='none'
        self.current_route={}
        self.current_edge=None
        self.is_on_current_route=False
        rospy.on_shutdown(self._on_shutdown)
        rospy.Subscriber('/current_node', String, self.node_callback)
        rospy.Subscriber('/current_edge', String, self.edge_callback)
        self.load_bag_info()
        rospy.loginfo("All Done ...")
        rospy.spin()

    def edge_callback(self, data):
        d={}
        try:
            clock = rospy.wait_for_message('/clock', Clock, timeout=10.0)
        except rospy.ROSException :
            rospy.logwarn("Failed to get clock")
            clock = 'null'
            return
        
        #print data, clock
        if data.data != 'none':# and clock != 'null':
            d['edge']=data.data
            d['start_time']=clock.clock.secs
            self.current_edge=d
        elif self.current_edge:
            #self.bag_data['edges_traversed'].append(d)
            self.current_edge['end_time']=clock.clock.secs
            self.current_edge['date'] = datetime.datetime.fromtimestamp(self.current_edge['start_time']).strftime('%Y-%m-%d_%H-%M-%S')
            self.current_edge['duration'] = self.current_edge['end_time']-self.current_edge['start_time']
            self.current_edge['name']=self.current_edge['edge'].rsplit('--')[0]+'--'+self.current_edge['date']
            self.bag_data['edges_traversed'].append(self.current_edge)
            self.current_edge=None

    def node_callback(self, data):
        d={}
        try:
            clock = rospy.wait_for_message('/clock', Clock, timeout=10.0)
        except rospy.ROSException :
            rospy.logwarn("Failed to get clock")
            clock = 'null'
#            return
        
        if data.data != 'none' and clock != 'null':
            self.nnodes_visited+=1
            d['node']=data.data
            d['clock']=clock.clock.secs
            d['date'] = datetime.datetime.fromtimestamp(clock.clock.secs).strftime('%Y-%m-%d_%H-%M-%S')
            self.bag_data['nodes_visited'].append(d)
            #print d
            
            if data.data == 'ChargingPoint':
                self.times_at_charging+=1
                if self.is_on_current_route:
                    print 'route ended'
                    self.current_route['finished']=clock.clock.secs
                    self.current_route['duration']=self.current_route['finished']-self.current_route['started']
                    self.current_route['timestamp']=(self.current_route['finished']+self.current_route['started'])/2
                    self.current_route['date'] = datetime.datetime.fromtimestamp(self.current_route['timestamp']).strftime('%Y-%m-%d_%H-%M-%S')
                    self.current_route['start_date'] = datetime.datetime.fromtimestamp(self.current_route['started']).strftime('%Y-%m-%d_%H-%M-%S')
                    self.current_route['end_date'] = datetime.datetime.fromtimestamp(self.current_route['finished']).strftime('%Y-%m-%d_%H-%M-%S')
                    self.bag_data['routes'].append(self.current_route)
                    self.current_route={}
                    self.is_on_current_route=False
            else:
                if self.prev_node == 'ChargingPoint':
                    if not self.is_on_current_route:        
                        print 'route started'
                        self.is_on_current_route=True
                        self.current_route['started']=clock.clock.secs
            self.prev_node = data.data

    def load_bag_info(self):
        infos= glob.glob("./*.bag.yaml")
        for i in infos:
            with open(i, 'r') as f:
                info = yaml.load(f)
                filtered_info={}
                filtered_info['path']=info['path']
                filtered_info['start']=info['start']
                filtered_info['end']=info['end']
                filtered_info['edge_messages']=0
                filtered_info['node_messages']=0
                for j in info['topics']:
                    if j['topic'] == '/current_edge':
                        filtered_info['edge_messages']=j['messages']
                    if j['topic'] == '/current_node':
                        filtered_info['node_messages']=j['messages']
                
                self.bag_data['bag_info'].append(filtered_info)


    def _on_shutdown(self):
        self.extract_routes()
        self._write_output()
        
    def extract_routes(self):
        self.bag_data['bag_info'].sort()
        for i in self.bag_data['routes']:
            i['bags']=[]
            start_bag_found=False
            for j in self.bag_data['bag_info']:
                if not start_bag_found:
                    if i['started'] > j['start'] and i['started'] < j['end']:
                        i['bags'].append(j['path'])
                        if i['finished'] < j['end']:
                            break
                        else:
                            start_bag_found=True
                else:
                    i['bags'].append(j['path'])
                    if i['finished'] < j['end']:                    
                        break
        
        for i in self.bag_data['edges_traversed']:
            i['bags']=[]
            start_bag_found=False
            for j in self.bag_data['bag_info']:
                if not start_bag_found:
                    if i['start_time'] > j['start'] and i['start_time'] < j['end']:
                        i['bags'].append(j['path'])
                        if i['end_time'] < j['end']:
                            break
                        else:
                            start_bag_found=True
                else:
                    i['bags'].append(j['path'])
                    if i['end_time'] < j['end']:                    
                        break

        
        
    def _write_output(self):
        self.bag_data['waypoints_visited']=self.nnodes_visited
        self.bag_data['times_at_charger']=self.times_at_charging
        self.bag_data['traversed_edges']=len(self.bag_data['edges_traversed'])
        yml = yaml.safe_dump(self.bag_data, default_flow_style=False)
        print "Creating output"
        fh = open("day_info.yml", "w")
        #s_output = str(bson.json_util.dumps(nodeinf, indent=1))
        s_output = str(yml)
        fh.write(s_output)
        fh.close 


if __name__ == '__main__':
    rospy.init_node('extract_info')
    server = infoExtract()