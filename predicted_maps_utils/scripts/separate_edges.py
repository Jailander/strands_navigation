#!/usr/bin/env python

#import sys
import yaml
import glob
import os

class separate_edges(object):

    def __init__(self) :
        self.list_of_edges=[]
        self.get_filenames()
        for i in self.list_of_edges:
            print i
        self.create_and_sort_in_folders()


    def create_and_sort_in_folders(self):
        for i in self.list_of_edges:
            folder_name=i
            print 'Creating folder: '+folder_name
            try:
                os.stat(folder_name)
            except:
                os.mkdir(folder_name)
            cmd = 'mv '+folder_name+'*.* '+folder_name
            print cmd
            os.system(cmd)

    def get_filenames(self):
        infos= glob.glob("./*.zip")
        infos.sort()
        for i in infos:
            name=i.rsplit('--')[0].lstrip('./')
            if name not in self.list_of_edges:
                self.list_of_edges.append(name)
        
        #infos2=glob.glob("./*/")
        

if __name__ == '__main__':
    server = separate_edges()