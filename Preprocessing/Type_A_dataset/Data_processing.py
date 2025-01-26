#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 23:20:12 2022

@author: monda089
"""
from collections import Counter
import numpy as np
import os
import math
## define the class here
class Dataset_processing():
    def __init__(self,name):
        self.name=name
        print("Currently processing dataset:",self.name)
    def create_adj_list(self,name,vertices):
        self.file_name=name
        self.vertices=vertices
        graph_file=open(self.file_name+".txt")
        lines = graph_file.readlines()
       
        node_alloc_dict={} ## dictoionary for allocation of edges to partitions
        for m in range(1,self.vertices):
                node_alloc_dict[m]=set()
        line_cnt=0
        for line in lines:
              #print(line)
              line_cnt +=1
              str_1 = line.split(",")
              #print(str_1)
              if(int(str_1[0]) in node_alloc_dict):
                  #print('yes')
                  node_alloc_dict[int(str_1[0])].add(int(str_1[1]))
                  node_alloc_dict[int(str_1[1])].add(int(str_1[0]))
        print(line_cnt)         
        ## conversion to list from set
        for key_dict in node_alloc_dict:
            node_alloc_dict[key_dict]=list(node_alloc_dict[key_dict])
        adj_list=list(node_alloc_dict.values())
        
        if (os.path.isfile(self.file_name+"METIS")=="False"):
            print("creating a new directory")
            os.makedirs(self.file_name+"METIS")
            with open("./"+self.file_name+"METIS"+"/"+self.file_name+"shifted_by_1.graph", 'w') as file:
                for item in adj_list:
                    for element in item:
                        file.write("%i" % element)
                        file.write(" ")
                    file.write("\n")
        else:
            print("Already found a directory")
            print(self.file_name+"METIS")
            with open(self.file_name+"shifted_by_1.graph", 'w') as file:
                for item in adj_list:
                    for element in item:
                        file.write("%i" % element)
                        file.write(" ")
                    file.write("\n")
        return adj_list, node_alloc_dict

## create object
# graph=Dataset_processing("PROTEINS_full_A")
# adj_list=graph.create_adj_list("PROTEINS_full_A",43472)

Total_vertices=372474+1

graph=Dataset_processing("COLLAB_A")
adj_list=graph.create_adj_list("COLLAB_A",Total_vertices)



class node_property():
    def __init__(self, neighbor_list, node_identity, total_edges, partition_id,cluster_id,intra_sub_cluster_edge,inter_sub_cluster_edge,inter_cluster_edge,intra_SC_dict={}, inter_SC_dict={}, inter_C_dict={},cluster_sent_list=[]):
        self.neighbor_list= neighbor_list
        self.node_identity=node_identity
        self.total_edges=total_edges
        self.partition_id=partition_id
        self.cluster_id=cluster_id
        ## for edge count
        self.intra_sub_cluster_edge=intra_sub_cluster_edge
        self.inter_sub_cluster_edge=inter_sub_cluster_edge
        self.inter_cluster_edge=inter_cluster_edge
        # dictionaries for vertex profiling
        self.intra_SC_dict=intra_SC_dict
        self.inter_SC_dict=inter_SC_dict
        self.inter_C_dict=inter_C_dict
        self.cluster_sent_list=cluster_sent_list
        self.sub_graph_presence = list()
        
# creation of the  array of the object
node_object_list=[]
for j in range(1,len(adj_list[1])+1):
    a=adj_list[1][j]
    node_object_list.append(node_property(a,j,len(a),0,0,0,0,0))

import math
def num_clsuters_required(buffer_size,feature_size,num_vertices):
    input_buffer=buffer_size
    feature_vect_size=feature_size
    num_feats_per_partition= math.floor(input_buffer/feature_vect_size)
    total_vertices_num=num_vertices
    if(num_feats_per_partition >= math.ceil(0.5*total_vertices_num)):
        print("single machine is good enough")
        cluster_num=1
    else:
        print("at least two machines required")
        print("select between partition 2, 4, 8 or 16")
        if (num_feats_per_partition >= math.ceil(0.25*total_vertices_num)):
            cluster_num=2
        else:
            if(num_feats_per_partition >= math.ceil(0.125*total_vertices_num)):
                cluster_num=4
            else:
                if(num_feats_per_partition >= math.ceil(0.0625*total_vertices_num)):
                    cluster_num=8
                else:
                    cluster_num=16
    return cluster_num

cluster_num=num_clsuters_required(512*1024, 16,Total_vertices)
cluster_num_second=num_clsuters_required(512*1024, 2,Total_vertices)

cluster_num=min(cluster_num,cluster_num_second)


if cluster_num > 1:
    newlist = node_object_list
 
    a_file = open("SW-620H_4_clusters.txt") ## reding the output from rabbit order
    count=0
    lines = a_file.readlines()
    for line in lines:
          str = line.split()
          newlist[count].cluster_id=int(str[0]) ## apeeding the clusted id data
          newlist[count].cluster_sent_list=[]
          count+=1      

    vertices = newlist

    vert = [[]]
    for k in range(len(vertices)): ## need to discuss
        lenk = len(vert)
        if (lenk <= vertices[k].cluster_id):
            for i in range(lenk, vertices[k].cluster_id + 1):
                vert.append([]);
        vert[vertices[k].cluster_id].append(vertices[k])
    
    num_mach = len(vert)
    print("num_mach : ", num_mach)  ## checking for the total number of clusters 
    
    import copy
    newlist_2=copy.deepcopy(newlist) ## deep copy to create seperate copy for refernce
    newlist_2 = sorted(newlist, key=lambda x: x.total_edges, reverse=True) ## sorting the newly created copy
    
    import time
    start_time=time.time()
    prev_id_list = dict()
    previous_id_list=[] ## for holding id prior to conversion for sorted graph
    new_id_list=[] ## for holding the newly assigned ids for the sprted graph
    #new_features=np.zeros((features_x,features_y))
    for i in range (len(newlist_2)):
        previous_id_list.append(newlist_2[i].node_identity)## getting the ids prior to ordering --> later will be used for mapping
        prev_id_list[newlist_2[i].node_identity] = i
        # new_features[i]=(feats_1[newlist_2[i].node_identity])
        new_id_list.append(i)
        newlist_2[i].node_identity=i ## assiging new ids to the sources accoroding to order by degree
        
    new_neighbor_list_of_list=[] ## for holding the converted list of all the nodesstart_time = time.time()
    for item_k in newlist_2:
        #print("NODE ID:",item_k.node_identity)
        new_neighbor_list=[] ## for holding the converted list of a node
        for item_r in item_k.neighbor_list:
            if item_r in prev_id_list:
                new_neighbor_list.append(prev_id_list[item_r])
    
                  
        new_neighbor_list_of_list.append(new_neighbor_list)    
           
    end_time=time.time()
    
    print(end_time-start_time, len(new_neighbor_list_of_list))             
    for number in range(len(newlist_2)):
        newlist_2[number].neighbor_list=new_neighbor_list_of_list[number]   ## over writing the old neighbor fist for the all the nodes    
        
    import pickle as pkl
    pkl.dump( newlist_2, open("Dumped_SW-620H_A_4_clusters.p", "wb" ) )
    
    vertices=newlist_2

    vert = [[]]
    for k in range(len(vertices)): ## need to discuss
        lenk = len(vert)
        if (lenk <= vertices[k].cluster_id):
            for i in range(lenk, vertices[k].cluster_id + 1):
                vert.append([]);
        vert[vertices[k].cluster_id].append(vertices[k])
    
    num_mach = len(vert)
    print("num_mach : ", num_mach)  ## checking for the total number of clusters
    
    for c in vertices:
      c.inter_cluster_edge_list = [0 for _ in range(num_mach)] ### _ ?
      c.inter_cluster_edge=0
      ### for reassignment
      c.new_inter_cluster_edge_list = [0 for _ in range(num_mach)] ### _ ?
      c.new_inter_cluster_edge=0
      c.new_cluster_id=0
      for nbr in c.neighbor_list:
        nbr_cid = vertices[nbr].cluster_id
        if c.cluster_id != nbr_cid:
          c.inter_cluster_edge_list[nbr_cid] += 1 ## adding to inter_cluster dictionary?
          c.inter_cluster_edge += 1

    inter_cluster_edge_count_top=[]
    for item_1 in vert:
        inter_cluster_edge_count= [0 for _ in range(num_mach)]
        for item_2 in item_1:
            for i in range (len(item_2.inter_cluster_edge_list)):
                inter_cluster_edge_count[i]+=item_2.inter_cluster_edge_list[i]
        inter_cluster_edge_count_top.append(inter_cluster_edge_count) 
        
    for item in inter_cluster_edge_count_top:
        print(item)
        
    for item in vert:
        print(len(item))  
else:
    print("create a singe cluster data")

    newlist = node_object_list
    vertices = newlist
    
    ### two sets of vertices
    vert = [[]]
    for k in range(len(vertices)): ## need to discuss
        lenk = len(vert)
        if (lenk <= vertices[k].cluster_id):
            for i in range(lenk, vertices[k].cluster_id + 1):
                vert.append([]);
        vert[vertices[k].cluster_id].append(vertices[k])
    
    num_mach = len(vert)
    print("num_mach : ", num_mach)  ## checking for the total number of clusters 
    
    
    
    import copy
    newlist_2=copy.deepcopy(newlist) ## deep copy to create seperate copy for refernce
    newlist_2 = sorted(newlist, key=lambda x: x.total_edges, reverse=True) ## sorting the newly created copy
    
    import time
    start_time=time.time()
    prev_id_list = dict()
    previous_id_list=[] ## for holding id prior to conversion for sorted graph
    new_id_list=[] ## for holding the newly assigned ids for the sprted graph
    #new_features=np.zeros((features_x,features_y))
    for i in range (len(newlist_2)):
        previous_id_list.append(newlist_2[i].node_identity)## getting the ids prior to ordering --> later will be used for mapping
        prev_id_list[newlist_2[i].node_identity] = i
        # new_features[i]=(feats_1[newlist_2[i].node_identity])
        new_id_list.append(i)
        newlist_2[i].node_identity=i ## assiging new ids to the sources accoroding to order by degree
        
    new_neighbor_list_of_list=[] ## for holding the converted list of all the nodesstart_time = time.time()
    for item_k in newlist_2:
        #print("NODE ID:",item_k.node_identity)
        new_neighbor_list=[] ## for holding the converted list of a node
        for item_r in item_k.neighbor_list:
            if item_r in prev_id_list:
                new_neighbor_list.append(prev_id_list[item_r])
    
                  
        new_neighbor_list_of_list.append(new_neighbor_list)    
           
    end_time=time.time()
    
    print(end_time-start_time, len(new_neighbor_list_of_list))             
    for number in range(len(newlist_2)):
        newlist_2[number].neighbor_list=new_neighbor_list_of_list[number]   ## over writing the old neighbor fist for the all the nodes    
        
    import pickle as pkl
    
    pkl.dump( newlist_2, open( "Dumped_DD_A_singe_cluster_ORDERED_METIS.p", "wb" ) )
    
    vertices=newlist_2
    
    # count_2=0
    # for item in vertices:
    #     if (item.cluster_id==2): 
    #         count_2+=1
    
    ### two sets of vertices
    vert = [[]]
    for k in range(len(vertices)): ## need to discuss
        lenk = len(vert)
        if (lenk <= vertices[k].cluster_id):
            for i in range(lenk, vertices[k].cluster_id + 1):
                vert.append([]);
        vert[vertices[k].cluster_id].append(vertices[k])
    
    num_mach = len(vert)
    print("num_mach : ", num_mach)  ## checking for the total number of clusters
    
    for c in vertices:
      c.inter_cluster_edge_list = [0 for _ in range(num_mach)] ### _ ?
      c.inter_cluster_edge=0
      ### for reassignment
      c.new_inter_cluster_edge_list = [0 for _ in range(num_mach)] ### _ ?
      c.new_inter_cluster_edge=0
      c.new_cluster_id=0
      for nbr in c.neighbor_list:
        nbr_cid = vertices[nbr].cluster_id
        if c.cluster_id != nbr_cid:
          c.inter_cluster_edge_list[nbr_cid] += 1 ## adding to inter_cluster dictionary?
          c.inter_cluster_edge += 1
    
    
    # count_1_3=0
    # for item in vert[0][0].neighbor_list:
    #     if (vertices[item].cluster_id==3):
    #         count_1_3+=1
            
    ########################
    inter_cluster_edge_count_top=[]
    for item_1 in vert:
        inter_cluster_edge_count= [0 for _ in range(num_mach)]
        for item_2 in item_1:
            for i in range (len(item_2.inter_cluster_edge_list)):
                inter_cluster_edge_count[i]+=item_2.inter_cluster_edge_list[i]
        inter_cluster_edge_count_top.append(inter_cluster_edge_count) 
        
    for item in inter_cluster_edge_count_top:
        print(item)
        
    for item in vert:
        print(len(item))
