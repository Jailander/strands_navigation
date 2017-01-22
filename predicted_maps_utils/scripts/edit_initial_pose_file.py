#!/usr/bin/env python

import json
import yaml
import sys


if __name__ == '__main__':
    if len(sys.argv) < 2 :
        print "usage: blah input_file.yaml"
	sys.exit(2)

    filename=str(sys.argv[1])
    mess=[]

    print "loading %s"%filename
    yaml_data=open(filename, "r")
    
    data = yaml.load_all(yaml_data)
    
    print "printing vlaa"
    for i in data:
        print i
        #yml = yaml.dump(i, canonical=True)
        print "------"
        #print yml
        mess.append(i)
    
    mess[0]['header']['frame_id']= 'amap'
    print mess[0]
    yml = yaml.dump(mess[0], default_flow_style=False)
    print yml
    
    fh = open(filename, "w")
    #s_output = str(bson.json_util.dumps(nodeinf, indent=1))
    s_output = str(yml)
    fh.write(s_output)
    fh.close
    