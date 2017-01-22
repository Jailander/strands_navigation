#! /usr/bin/env python

import os
#import sys
import yaml
import glob
from datetime import datetime
import rospy
# Brings in the SimpleActionClient
#import std_msgs #.msg import String

#import cv2
#import numpy as np

def load_yaml(filename):
    #rospy.loginfo("loading %s"%filename)
    with open(filename, 'r') as f:
        return yaml.load(f)

class stitcher(object):
    
    def __init__(self) :
        self.endexec= False
        #rospy.on_shutdown(self._on_node_shutdown)
        filenames=[]

        yaml_info = load_yaml('base_map.yaml')
        print yaml_info
        
        files = glob.glob('./*.pgm')
        print files
        for i in files:
            namestr = (i[2:])[:-4]
            print namestr
            if namestr != 'base_map':
                filenames.append(namestr)

        #self.create_folder('stitched_maps')
        #self.create_folder('processed')
        
        for i in filenames:
            yaml_cpy = yaml_info
            #sepoch = i.rsplit('--')[1].rstrip('.pgm')
            #epoch = (datetime.strptime(sepoch,"%Y-%m-%d_%H-%M-%S")).strftime('%s')
            epoch = (datetime.strptime(i,"%Y-%m-%d_%H-%M-%S")).strftime('%s')
            epochname = i.rsplit('--')[0].lstrip('./')+'-'+str(epoch)+'.pgm'
            print i, epoch, epochname
            yaml_cpy['image']=epochname
            yamlfilename = epochname+'.yaml'
            #yml = yaml.safe_dump(yaml_cpy, default_flow_style=False)
            yml = yaml.safe_dump(yaml_cpy)
            fh = open(yamlfilename, "w")
            s_output = str(yml)
            print s_output
            fh.write(s_output)
            fh.close
            stitchcmdstr = 'rosrun mapstitch mapstitch -o '+epochname+' base_map.pgm '+i+'.pgm'
            #mvcmdstr = 'mv '+epoch+'.* ./stitched_maps/'
            #mvcmdstr2 = 'mv '+i+'.* ./processed/'
            print stitchcmdstr
            os.system(stitchcmdstr)
            #print mvcmdstr
            #os.system(mvcmdstr)
            #print mvcmdstr2
            #os.system(mvcmdstr2)


    def create_folder(self, name):
        folder_name=name
        print 'Creating folder: '+folder_name
        try:
            os.stat(folder_name)
        except:
            os.mkdir(folder_name)
    
#    def _on_node_shutdown(self):
#        self.endexec= True
        #sleep(2)


if __name__ == '__main__':
#    print 'Argument List:',str(sys.argv)
#    if len(sys.argv) < 2 :
#	sys.exit(2)
    #rospy.init_node('stitcher')
    ps = stitcher()