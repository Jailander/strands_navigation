#!/usr/bin/env python
# license removed for brevity

import os
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int64
from nav_msgs.msg import OccupancyGrid



class predicted_map_saver(object):

    def __init__(self) :
        self.first_charge=True
        rospy.on_shutdown(self._on_node_shutdown)
        self.map_name_pub = rospy.Publisher('/mapName', String, latch=True, queue_size=1)
        self.map_time_pub = rospy.Publisher('/addTime', Int64, latch=True, queue_size=1)
        self.map_save_pub = rospy.Publisher('/route_map', OccupancyGrid, latch=True, queue_size=1)

        self.pred_time_pub = rospy.Publisher('/predictTime', Int64, latch=True, queue_size=1)
        self.pred_ord_pub = rospy.Publisher('/predictOrder', Int64, latch=True, queue_size=1)
        rospy.Subscriber('/current_node', String, self.current_node_callback)

        rospy.spin()

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
            rospy.sleep(2.0)
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
        
        

    def _on_node_shutdown(self):
        print "BYE"

if __name__ == '__main__':
    rospy.init_node('predicted_map_saver')
    server = predicted_map_saver()
