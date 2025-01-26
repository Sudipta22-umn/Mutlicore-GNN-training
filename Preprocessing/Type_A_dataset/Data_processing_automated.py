#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 12:12:46 2022

@author: monda089
"""
import os
import shutil
import pickle as pkl


#from Data_processing import Dataset_processing

class Data_processing_auto ():
    def __init__(self,name):
        self.name=name
        print("Currently processing dataset:",self.name)
    def create_adj_list(self,name,vertices):
        self.file_name=name
        self.vertices=vertices+1
        self.cwd=os.getcwd()
        self.adj_list_dir=os.path.join(self.cwd,self.file_name)
       
        
        graph_file=open(self.adj_list_dir+"/"+self.file_name+"_A"+".txt")
        print(self.adj_list_dir+"/"+self.file_name)
        print(os.path.isfile(self.adj_list_dir+"/"+self.file_name+"METIS"))
        
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
        
         
        if (os.path.isfile(self.adj_list_dir+"/"+"/METIS")==False):
            print("creating a new directory")
            shutil.rmtree(self.adj_list_dir+"/"+"/METIS")
            os.makedirs(self.adj_list_dir+"/"+"/METIS")
            with open(self.adj_list_dir+"/"+"/METIS"+"/"+self.file_name+"shifted_by_1.graph", 'w') as file:
                for item in adj_list:
                    for element in item:
                        file.write("%i" % element)
                        file.write(" ")
                    file.write("\n")
        else:
            print("Already found a directory")
            print(self.file_name+"METIS")
            # with open(self.file_name+"shifted_by_1.graph", 'w') as file:
            #     for item in adj_list:
            #         for element in item:
            #             file.write("%i" % element)
            #             file.write(" ")
            #         file.write("\n")
        return adj_list

dataset = [
	

 		  
		('OVCAR-8H'                  , 66       , 2, 1890931) , 
 		('Yeast'                     , 74       , 2, 1714644) ,
		('DD'                        , 89       , 2, 334925) ,
		('TWITTER-Real-Graph-Partial', 1323     , 2, 580768) ,   
 		('SW-620H'                   , 66       , 2, 1889971) ,

		
]

adj_dict={}
for data, input_dim, output_dim, total_vertices in dataset:
    print(data)
    if data not in adj_dict:
            data_obj=Data_processing_auto(data)
            adj_dict[data]=data_obj.create_adj_list(data,total_vertices+1)
            #adj_dict[data].append(data_obj.create_adj_list(data,total_vertices+1))

    


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
        
#creation of the  array of the object
node_obj_dict={}
for k,v in adj_dict.items():
    node_object_list=[]
    print(len(v))
    print(type(v))
    for j in range(0,len(v)):
        a=v[j]
        node_object_list.append(node_property(a,j+1,len(a),0,0,0,0,0))
    #print(adj_dict[k])
    if k not in node_obj_dict:
        node_obj_dict[k]=node_object_list
    #adj_dict[k].append(node_object_list)

import csv
for k,v in adj_dict.items():
    list_of_neighbors=[]
    for j in range(0,len(v)):
        list_of_neighbors.append(v[j])
    data1 = list_of_neighbors
    with open(k+"_neighborhood.csv", "w", newline="") as f:
        writer= csv.writer(f)
        writer.writerows(data1)

import csv
for k,v in adj_dict.items():
    num_neighbors=[]
    for j in range(0,len(v)):
        num_neighbors.append(len(v[j]))
    data1 = num_neighbors
    with open(k+"_degree.csv", "w", newline="") as f:
        writer= csv.writer(f)
        writer.writerows(map(lambda x: [x], data1))
        
cluster_num_dict={}
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

for data, input_dim, output_dim, total_vertices in dataset:
    print(data)
    cluster_num=num_clsuters_required(512*1024, 64,total_vertices)
    cluster_num_second=num_clsuters_required(512*1024, 2,total_vertices)
    cluster_num=min(cluster_num,cluster_num_second)
    if data not in cluster_num_dict:
        cluster_num_dict[data]=cluster_num
        
        
##


    
for key,val in cluster_num_dict.items():
    if  val > 1:
        print("create a singe cluster data")
        print("Datset name:",key)
        print("cluster number:",val)
        cwd=os.getcwd()
        newlist = node_obj_dict[key]
        a_file=open(key+"_"+str(val)+"_clusters.txt","r")
        
        # if(k=="Yeast"):
        #     newlist = node_obj_dict[k]
        #     a_file=open(k+"_"+str(v)+"_clusters.txt","r")
        #     #a_file =open('Yeast_4_clusters.txt') ## reding the output from rabbit order
        # if (k=="TWITTER-Real-Graph-Partial"):
        #     a_file =open('TWITTER-Real-Graph-Partial_2_clusters.txt') ## reding the output from rabbit order
        # if (k=="SW-620H"):
        #     a_file =open('SW-620H_4_clusters.txt') ## reding the output from rabbit order
            
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
            
        
        pkl.dump( newlist_2, open(key+"_clusters_ORDERED_METIS.p", "wb" ) )
        # if(k=="Yeast"):
        #     pkl.dump( newlist_2, open(k+"_4_clusters_ORDERED_METIS.p", "wb" ) )
        # if (k=="TWITTER-Real-Graph-Partial"):
        #     pkl.dump( newlist_2, open("TWITTER-Real-Graph-Partial_2_clusters_ORDERED_METIS.p", "wb" ) )
        # if (k=="SW-620H"):
        #     pkl.dump( newlist_2, open("SW-620H_4_clusters_ORDERED_METIS.p", "wb" ) )
      
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
        print("Datset name:",key)
        print("cluster number:",val)
        newlist = node_obj_dict[key]
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
            
        
        pkl.dump( newlist_2, open(key+"_single_ORDERED_METIS.p", "wb" ) )
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

