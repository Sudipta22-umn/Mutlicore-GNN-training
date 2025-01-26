#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 19:14:54 2022

@author: monda089
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 12:37:16 2022

@author: monda089
"""


# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 12:12:46 2022

@author: monda089
"""
import os
import shutil
import pickle as pkl
import os
import math



def process_vertices(vertices,num_mach):
    for c in vertices:
      c.inter_cluster_edge_list = [0 for _ in range(num_mach)] ### _ ?
      c.inter_cluster_edge=0
      for nbr in c.neighbor_list:
        nbr_cid = vertices[nbr].cluster_id
        if c.cluster_id != nbr_cid:
          c.inter_cluster_edge_list[nbr_cid] += 1 ## adding to inter_cluster dictionary?
          c.inter_cluster_edge += 1
      c.inter_cluster_edge_cnt = [c.inter_cluster_edge_list[:], c.inter_cluster_edge_list[:]]
      c.inter_cluster_edge_list[c.cluster_id]=c.total_edges-c.inter_cluster_edge
    return vertices
                       
def inter_cluster_edge_track(vert,num_mach):
    inter_cluster_edge_count_top=[]
    for item_1 in vert:
        inter_cluster_edge_count= [0 for _ in range(num_mach)]
        for item_2 in item_1:
            for i in range (len(item_2.inter_cluster_edge_list)):
                inter_cluster_edge_count[i]+=item_2.inter_cluster_edge_list[i]
        inter_cluster_edge_count_top.append(inter_cluster_edge_count) 
    return inter_cluster_edge_count_top

def inter_cluster_edge_per_machine(inter_cluster_edge_count):
    inter_cluster_edge_per_machine=[]
    count=0
    for item in inter_cluster_edge_count:
        print(item)
        k=0
        for z in range(len(item)):
            if z!=count:
                k+=item[z]
        inter_cluster_edge_per_machine.append(k)
        count+=1    
    return inter_cluster_edge_per_machine


def vertex_reassign(vert,diff,partition_frac,trans_c, vertices):
    for item in vert:#[0:math.ceil(diff/partition_frac)]:
          if(math.ceil(item.inter_cluster_edge_list[item.cluster_id]/2) < item.inter_cluster_edge_list[trans_c]):## tryin to include the intra cluster edge
            
            for item_n in item.neighbor_list:
                nbr=vertices[item_n]
                if (nbr.cluster_id==item.cluster_id): ## previously in the same cluster
                    nbr.inter_cluster_edge_list[item.cluster_id]-=1
                    #item.inter_cluster_edge_list[item.cluster_id]-=1
                    ###increase the inter cluster edges
                    nbr.inter_cluster_edge_list[trans_c]+=1
                    #item.inter_cluster_edge_list[trans_c]+=1
                    
                if (nbr.cluster_id==trans_c):
                    nbr.inter_cluster_edge_list[trans_c]=+1
                    #item.inter_cluster_edge_list[trans_c]=+1
                    ## decrease the inter cluster edge
                    nbr.inter_cluster_edge_list[item.cluster_id]-=1
                    
                    
            item.cluster_id=trans_c
            vert[trans_c].append(item)
            vert[1].remove(item)
                    
    return vert

#from Data_processing import Dataset_processing

src_list=[]
dst_list=[]

class Data_processing_auto ():
    def __init__(self,name):
        self.name=name
        print("Currently processing dataset:",self.name)
    def create_adj_list(self,name,vertices):
        self.file_name=name
        self.vertices=vertices
        self.cwd=os.getcwd()
        #self.adj_list_dir=os.path.join(self.cwd,self.file_name)
       
        
        graph_file=open(self.cwd+"/"+self.file_name+".txt")
        # print(self.adj_list_dir+"/"+self.file_name)
        # print(os.path.isfile(self.adj_list_dir+"/"+self.file_name+"METIS"))
        
        lines = graph_file.readlines()
        
        # for line in lines:
        #     str_2=line.split("\t")
        #     src_list.append(str_2[0])
        #     dst_list.append(str_2[1])
       
        node_alloc_dict={} ## dictoionary for allocation of edges to partitions
        for m in range(0,self.vertices):
                node_alloc_dict[m]=set()
        line_cnt=0
        for line in lines:
              # print(line)
              #print(line)
            line_cnt +=1
            str_1 = line.split()
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
        ## filter out the vertices with zero edges
     
        print("number of vertices:", vertices)
        

        ##edge_cnt
        edge_cnt=0
        for item in adj_list:
            edge_cnt=edge_cnt+len(item)
        edge_cnt_metis=edge_cnt/2    
                
        if (os.path.isfile(f'{self.cwd}/METIS_type_3/{self.file_name}')==False):
            print("creating a new directory")
            shutil.rmtree(f'{self.cwd}/METIS_type_3/{self.file_name}', ignore_errors= True)
            os.makedirs(f'{self.cwd}/METIS_type_3/{self.file_name}', exist_ok=True)
            with open(f'{self.cwd}/METIS_type_3/{self.file_name}/{self.file_name}.graph', 'w') as file:
                file.write(str(vertices)+" "+str(edge_cnt_metis))
                file.write("\n")
                for item in adj_list:
                    new_list = [x+1 for x in item]
                    for element in new_list:
                        file.write("%i" % element)
                        file.write(" ")
                    file.write("\n")
               
        else:
            print("Already found a directory")
            print(f'{self.cwd}/METIS_type_3/{self.file_name}')
            # with open(self.file_name+"shifted_by_1.graph", 'w') as file:
            #     for item in adj_list:
            #         for element in item:
            #             file.write("%i" % element)
            #             file.write(" ")
            #         file.write("\n")

        
        if vertices < 1e5:
            partition_num =1
            
        if vertices >= 1e5 and vertices < 2e5:
            partition_num =2
            
        if vertices >= 2e5 and vertices < 4e5:
            partition_num =2
            
        if vertices >= 4e5 and vertices < 1e6:
            partition_num =4
            
        if vertices >= 1e6 and vertices < 5e6:
            partition_num =16
            
        if vertices >= 5e6 and vertices <= 10e6:
            partition_num =36
        # METIS_file_path = str(self.cwd+"/METIS"+"/"+self.file_name+".graph")
        # print(METIS_file_path)
        # os.path.isfile(METIS_file_path)
        print('Running metis')
        os.system(f'~/local/bin/gpmetis {self.cwd}/METIS_type_3/{self.file_name}/{self.file_name}.graph {partition_num}')   
        return adj_list,edge_cnt



auto_dataset = [
	

# 		('PROTEINS_full'             , 29       , 2, 43471) ,   
# 		#('OVCAR-8H'                  , 66       , 2, 1890931) , 
		('amazon0505', 410236) ,
		('amazon0601', 403394) ,
# 		('socBlogCatalog',88785) ,
        ('comamazon', 548552) 

		
]


adj_dict={}
edge_dict={}
for data, total_vertices in auto_dataset:
    print(data)
    if data not in adj_dict:
            data_obj=Data_processing_auto(data)
            adj_dict[data],edge_dict[data]=data_obj.create_adj_list(data,total_vertices)
            
   

power_law_dict={}


    


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
        node_object_list.append(node_property(a,j,len(a),0,0,0,0,0))
    #print(adj_dict[k])
    if k not in node_obj_dict:
        node_obj_dict[k]=node_object_list
    #adj_dict[k].append(node_object_list)

for data, total_vertices in auto_dataset:
    power_law_dict[data]={}
    newlist = node_obj_dict[data]
    newlist_2 = sorted(newlist, key=lambda x: x.total_edges, reverse=True) ## sorting the newly created copy
    power_law_eval_list=[10,20]
    for item in power_law_eval_list:
        power_law_dict[data][item]=sum ([newlist_2[i].total_edges for i in range(math.ceil (len(newlist_2)/(100/item)) )]) / edge_dict[data]

import csv


for data, total_vertices in auto_dataset:
    
    if total_vertices < 1e5:
        val =1
    
    if total_vertices >= 1e5 and total_vertices < 2e5:
        val =2
        
    if total_vertices >= 2e5 and total_vertices < 4e5:
        val =2
        
    if total_vertices >= 4e5 and total_vertices < 1e6:
        val =4
        
    if total_vertices >= 1e6 and total_vertices < 5e6:
        val =16
        
    if total_vertices >= 5e6 and total_vertices <= 10e6:
        val =36
    print("create multi cluster data")
    print("Datset name:",data)
    print("cluster number:",val)
    cwd=os.getcwd()
    newlist = node_obj_dict[data]
    #a_file=open(data+"_"+str(val)+"_clusters.out","r")
    a_file=open(f'{cwd}/METIS_type_3/{data}/{data}.graph.part.{val}',"r")
    
    # if(k=="Yeast"):
    #     newlist = node_obj_dict[k]
    #     a_file=open(k+"_"+str(v)+"_clusters.out","r")
    #     #a_file =open('Yeast_4_clusters.out') ## reding the output from rabbit order
    # if (k=="TWITTER-Real-Graph-Partial"):
    #     a_file =open('TWITTER-Real-Graph-Partial_2_clusters.out') ## reding the output from rabbit order
    # if (k=="SW-620H"):
    #     a_file =open('SW-620H_4_clusters.out') ## reding the output from rabbit order
        
    count=0
    lines = a_file.readlines()
    for line in lines:
          str_1 = line.split()
          newlist[count].cluster_id=int(str_1[0]) ## apeeding the clusted id data
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
    #newlist_2=copy.deepcopy(newlist) ## deep copy to create seperate copy for refernce
    newlist_2 = newlist
    # import time
    # start_time=time.time()
    # prev_id_list = dict()
    # previous_id_list=[] ## for holding id prior to conversion for sorted graph
    # new_id_list=[] ## for holding the newly assigned ids for the sprted graph
    # #new_features=np.zeros((features_x,features_y))
    # for i in range (len(newlist_2)):
    #     previous_id_list.append(newlist_2[i].node_identity)## getting the ids prior to ordering --> later will be used for mapping
    #     prev_id_list[newlist_2[i].node_identity] = i
    #     # new_features[i]=(feats_1[newlist_2[i].node_identity])
    #     new_id_list.append(i)
    #     newlist_2[i].node_identity=i ## assiging new ids to the sources accoroding to order by degree
        
    # new_neighbor_list_of_list=[] ## for holding the converted list of all the nodesstart_time = time.time()
    # for item_k in newlist_2:
    #     #print("NODE ID:",item_k.node_identity)
    #     new_neighbor_list=[] ## for holding the converted list of a node
    #     for item_r in item_k.neighbor_list:
    #         if item_r in prev_id_list:
    #             new_neighbor_list.append(prev_id_list[item_r])
    
                  
    #     new_neighbor_list_of_list.append(new_neighbor_list)    
           
    # end_time=time.time()
    
    # print(end_time-start_time, len(new_neighbor_list_of_list))             
    # for number in range(len(newlist_2)):
    #     newlist_2[number].neighbor_list=new_neighbor_list_of_list[number]   ## over writing the old neighbor fist for the all the nodes    
        
    #z=open("/home/sachin00/monda089/GNN_data_processing/Type_III_data_processing"+key+"_"+str(val)+"_ORDERED_METIS.p","rb") 
    print(type(val))
    #pkl.dump( newlist_2, open(data+"_"+str(val)+"_ORDERED_METIS.p", "wb" ) )
    pkl.dump( newlist_2, open(f'{cwd}/processed_METIS_files_type_3/{data}_{val}_NOT_ORDERED_METIS.p', "wb" ) )
    
    
    #pkl.dump( newlist_2, open(key+"_ORDERED_METIS.p", "wb" ) )
    #pkl.dump( newlist_2, open(key+"_ORDERED_METIS_"+str(val)+"_"+".p", "wb" ) )
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
                
    vertices=process_vertices(vertices,num_mach)
                        
    inter_cluster_edge_count_top=inter_cluster_edge_track(vert, num_mach)
    
    
    inter_cluster_edge_per_machine_initial=[]
    inter_cluster_edge_per_machine_initial=inter_cluster_edge_per_machine(inter_cluster_edge_count_top)
    
            
    for item in vert:
        print(len(item))
        
    
    vertices=process_vertices(vertices,num_mach)
    inter_cluster_edge_count_top_re=inter_cluster_edge_track(vert,num_mach)
    
    ## different types of edges before processing begins
    total_intial_edges_per_machine=[0]*num_mach
    total_intial_intra_cluster_edges_per_machine=[0]*num_mach
    total_intial_inter_cluster_edges_per_machine=[0]*num_mach
    #off_chip_point=[0]*num_mach ## defining off-chip communication as an array [instead of a single value]
    off_chip_comm_ratio=[0]*num_mach
    
    for k in range(num_mach):
        # print(f'inter cluster edge of machine:{k} is: {sum(inter_cluster_edge_count_top_re[k])}')
        total_intial_edges_per_machine[k]=sum(inter_cluster_edge_count_top_re[k])
        total_intial_intra_cluster_edges_per_machine[k]=inter_cluster_edge_count_top_re[k][k]
        total_intial_inter_cluster_edges_per_machine[k]=total_intial_edges_per_machine[k]-total_intial_intra_cluster_edges_per_machine[k]
        #print(f'For machine :{k} the inter vs total ratio is :{total_intial_inter_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]}')
        #print(f'For machine :{k} the inter vs intra ratio is :{total_intial_intra_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]}')
        off_chip_comm_ratio[k]=total_intial_intra_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]
        print(f'For machine :{k} the off chip comm ratio is :{off_chip_comm_ratio[k]}')           
   


