#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 22:54:32 2022

@author: sudiptamondal
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 11:01:27 2022

@author: monda089
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 24 10:19:27 2022

@author: monda089

"""
## global function definition
import numpy as np
import sys

import pickle as pkl
from collections import Counter
import copy
import csv
import math
import os
import random

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
        self.inter_cluster_edge_list = list() ### added new
        self.inter_cluster_edge_cnt = list()
        self.inter_cluster_edge=inter_cluster_edge
        # dictionaries for vertex profiling
        self.intra_SC_dict=intra_SC_dict
        self.inter_SC_dict=inter_SC_dict
        self.inter_C_dict=inter_C_dict
        self.cluster_sent_list=cluster_sent_list
        self.sub_graph_presence = set()



### necessary functions deifinitions
def send_recieve_list (num_machines):
    numbers=list(range(num_machines))
    comb_list=[]
        
    from itertools import combinations
    v=list(combinations(numbers,2))
    for item in v:
        comb_list.append(list(item))
    
    
    
    final_pair_list=[]
    
    for i in range(num_machines-1):
     pair_list_per_round=[]
     for item in comb_list:
       
        if(len(pair_list_per_round)==0):
            pair_list_per_round.append(item)
            
        elif(len(pair_list_per_round)<(num_machines/2) and len(pair_list_per_round)>0):
            # print(item[0])
            # print(item[1])
            # print(pair_list_per_round)
          
            # element exists in listof listor not?
            res1 = any(item[0] in sublist for sublist in pair_list_per_round)
            res2 = any(item[1] in sublist for sublist in pair_list_per_round)
    
        
            if(res1 == False and res2 == False):
                pair_list_per_round.append(item)
            
        elif(len(pair_list_per_round)==num_machines/2):
            break
        
     for item_3 in pair_list_per_round:
         comb_list.remove(item_3)
         final_pair_list.append(item_3)     
    
    print(final_pair_list)    
    
    final_send_list=[]
    final_recive_list=[]
    
    for item in final_pair_list:
        final_send_list.append(item[0])
        final_recive_list.append(item[1])
    return final_send_list, final_recive_list



########
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

def buffer_config(buffer_size,num_clusters,total_vertices,feature_vect_size):
    
    buffer_size=buffer_size
    feature_vect_size=feature_vect_size
    num_clusters=num_clusters
    total_vertices=total_vertices
    ## examine the vertex data
    ## load vertex data
    vertices=pkl.load(open(dataset+"_"+str(num_clusters)+"_"+"ORDERED_METIS.p", "rb"))
    vert = [[]]
    for k in range(len(vertices)): ## need to discuss
        lenk = len(vert)
        if (lenk <= vertices[k].cluster_id):
            for i in range(lenk, vertices[k].cluster_id + 1):
                vert.append([]);
        vert[vertices[k].cluster_id].append(vertices[k])
        
    cluster_len_list=[]
    for item in vert:
        cluster_len_list.append(len(item))
    
        
    partition_num=[] ## can be single value or a choice of partititions
    buffer_cap=[] ## similarly this should also be a list
    
    num_features_per_cluster=min(cluster_len_list)
    print(f'num_features_per_cluster :{num_features_per_cluster}')
    
    num_feats_per_partition= math.floor(buffer_size/feature_vect_size)
    print(f' num_feats_per_partition : {num_feats_per_partition}')
    
    if (num_feats_per_partition >= num_features_per_cluster):
         if (num_features_per_cluster*feature_vect_size >= 256*1024):
            partition_num.append(1)
            buffer_cap.append(num_features_per_cluster*feature_vect_size)
         else:
            print("No buffer and cluster combination possible")
            partition_num=[] ## can be single value or a choice of partititions
            buffer_cap=[] #
                
    else:   
        for i in [4,8,16]:
            if (num_feats_per_partition <= math.ceil((1/i)*num_features_per_cluster)):
                partition_num.append(i)
                buffer_cap.append(i*num_feats_per_partition)
                
    return partition_num, buffer_cap


##################
dataset_info = [


# 		( 'amazon0505'               , 64	  , 22, 410236),
# 		( 'artist'                   , 64    , 12, 50515, 1),
# 		( 'com-amazon'               , 64	  , 22, 548552, 16),
# 		( 'soc-BlogCatalog'	         , 64    , 39, 88784, 4), 
		( 'amazon0601'  	         , 256	  , 22, 403394), 
]

num_cluster_list=[4]  
## top list to get the iteraton data out
data_list_per_buffer_and_partitions=[]

## call datasets in automated fashion
for dataset, hid_1, hid_2, total_vertices in dataset_info:
    for num_clusters in num_cluster_list:
        config_list=buffer_config(512*1024, num_clusters,total_vertices, hid_1)
        buffer_size_arr=[]    
        #########
        for element in config_list[1]:
            buffer_size_arr.append(element)
        inital_percentile_arr=[75]
        edge_percent_arr=[0.1]
        iter_iterval_arr=[5] ## 
        normal_iter_num=50
        
        num_element_processed_per_PE=8
        spad_width=64
        
        
        ## cycle count lists
        ## Normal mode
        ## Normal mode
        top_data_list=[]
        Normal_PE_cycle_list=[]
        Normal_off_chip_cycle_list=[]
        Normal_mem_stall_cycle_list=[]
        Normal_on_chip_cycle_list=[]
        Normal_total_cycle_list=[]
        Normal_total_cycle_list_mem_stall=[]
        ##
        Random_PE_cycle_list=[]
        Random_off_chip_cycle_list=[]
        Random_total_cycle_list=[]
        machine_6_on_chip_list_forward=[]
        
        top_data_list=[]
        config_cnt=0
        for buffer_cap in buffer_size_arr:
            config_cnt +=1
            for percentile_point in inital_percentile_arr:
                #for gamma_point_1 in gamma_point_1_arr:
                    for edge_percent in edge_percent_arr:
                        for iter_iterval in iter_iterval_arr:
                            print(f'buffer_cap:{buffer_cap}')
                            #print(percentile_point)
                            #print(f'percentile_point:{percentile_point}')
                            #print(gamma_point_1)
                            #print(f'gamma_point_1:{gamma_point_1}')
                            #print(off_chip_point)
                            print(f'edge_percent:{edge_percent}')
                            
                            print(f'iter_interval:{iter_iterval}')
                            
            
                           
                           
                            data_list_per_buffer_and_partitions=[]
                            folder_name = '_Feature_partition_num'+str(config_list[0][config_cnt-1])+'buffer_cap'+'_'+str(buffer_cap)+'_'+'percentile_point'+'_'+str(percentile_point)+'_'+'edge_percent'+'_'+str(edge_percent)+'_'+'iter_interval'+'_'+str(iter_iterval)
                            print(folder_name)
            
                            
                            #vertices = pkl.load(open( "save_amazon0601_node_object_list_4_cluster_ORDERED_reassigned_clusters_faster.p", "rb"))
                            
                            vertices= pkl.load(open(dataset+"_"+str(num_clusters)+"_"+"ORDERED_METIS.p", "rb"))
                          
                            for c in vertices:
                                if (len(c.neighbor_list)>=25):
                                    c.neighbor_list= random.sample(c.neighbor_list, 25)
                                    c.total_edges=25
                           
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
                                print(f'For machine :{k} the inter vs total ratio is :{total_intial_inter_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]}')
                                print(f'For machine :{k} the inter vs intra ratio is :{total_intial_intra_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]}')
                                off_chip_comm_ratio[k]=total_intial_intra_cluster_edges_per_machine[k]/total_intial_edges_per_machine[k]
                                print(f'For machine :{k} the off chip comm ratio is :{off_chip_comm_ratio[k]}')
                            
                            total_edges_done_per_machine=[0]*num_mach
                            total_intra_cluster_edges_done_per_machine=[0]*num_mach
                            total_inter_cluster_edges_done_per_machine=[0]*num_mach
                            
                            total_done_vs_total_ini=[0]*num_mach
                            total_intra_done_vs_total_intra_ini=[0]*num_mach
                            total_inter_done_vs_total_inter_ini=[0]*num_mach
                            
                            for item in vert:
                                print(len(item))
                            
                            inter_cluster_edge_per_machine_re=[]
                            inter_cluster_edge_per_machine_re=inter_cluster_edge_per_machine(inter_cluster_edge_count_top_re)
                            
                            ## opening a directory to write results
                            dir_name="GINConv_aggregation_"
                            sub_dir_name_1="num_part_4_and_5_data_nov_19_50_iters"+str(num_clusters)
                            sub_dir_name_2="dataset_"+dataset
                            
                            os.makedirs(os.path.join(dir_name,sub_dir_name_1,sub_dir_name_2,folder_name))
                                   
                            
                            ### initiate the simulation log file
                            sim_log = open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/simulation_log_amazon.txt", "a")
                            sim_log.write(f'buffer_cap:{buffer_cap}')
                            sim_log.write('\n')
                            sim_log.write(f'percentile_point:{percentile_point}')
                            sim_log.write('\n')
                            #sim_log.write(f'off_chip_point:{off_chip_point}')
                            #sim_log.write('\n')
                            machine_6_on_chip_log=open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/machine_6_on_chip_log.txt", "a")
                            ## making the initial subgraphs
                            sub_graph = []
                            for k in range(len(vert)):
                                sub_graph.append(vert[k][0:buffer_cap])
                            
                            print("input buffer capacity:",buffer_cap)
                            sim_log.write(f'input buffer capacity:{buffer_cap}')
                            sim_log.write('\n')
                            #gamma = [23,10,50,50]
                            gamma = [0]*num_mach
                            print("gamma:", gamma)
                            sim_log.write(f'gamma:{gamma}')
                            sim_log.write('\n')
                            
                            total_removal=0
                            dram_index = [buffer_cap for _ in range(num_mach)] ## for keeping track of dram index in off-chip access
                            all_nodes_done = True
                            iter = 0
                            #max_diff_list=[]
                            rem_list = [[] for _ in range(num_mach)]
                            removed_count_list = []
                            
                            ## for re-setting the sub_graph_presence of all vertices before the processing begins
                            for v in vertices:
                              v.sub_graph_presence = set()
                            ## for each sub graph assigned to each machine adding the machine id (k) to each vertex
                            for k in range(num_mach):
                              for v in sub_graph[k]:
                                v.sub_graph_presence.add(k)
                                
                            ## initialize variables
                            ## off-chip access count
                            dram_access_list=[0]*num_mach
                            ## on-chip access count
                            on_chip_comm_list=[0]*num_mach
                            ## list for cycle count
                            cycle_count_list=[0]*num_mach
                            ## list for counting rounds
                            round_count_list=[0]*num_mach
                            ##list for counting avg degree
                            avg_degree_list=[0]*num_mach
                            ########
                            ### setting off-chip comm ratio
                            #off_chip_comm_ratio=[1]*num_mach
                            ## list for cycle count
                            cycle_count_list=[0]*num_mach
                            ## total node processed list of list
                            total_node_processed_per_iter=[]
                            ## total on chip communication list
                            total_on_chip_comm_list_1=[]
                            total_on_chip_comm_list_2=[]
                            total_on_chip_comm_list=[]
                            #####
                            total_off_chip_comm_list=[]
                            total_off_chip_cycle_list=[]
                            total_off_chip_cycle_list_refetch=[]
                            total_num_refetch_list=[]
                            total_mem_stall_cycle_list=[]
                            ### added jan 14 ###
                            cycle_required_for_on_chip_comm_per_iter=[]
                            cycle_required_for_off_chip_comm_per_iter=[]
                            cycle_required_for_off_chip_comm_per_iter_refetch=[]
                            cycle_required_for_PE_computation_per_iter=[]
                            cycle_required_for_mem_stall_per_iter=[]
                            
                            removed_count_list=[]
                            y_list=[]
                            z_list=[]
                            
                            ###variables for keeping track percentage of edge counts
                            total_edges_done_per_machine=[0]*num_mach
                            total_intra_cluster_edges_done_per_machine=[0]*num_mach
                            total_inter_cluster_edges_done_per_machine=[0]*num_mach
                            
                            total_done_vs_total_ini=[0]*num_mach
                            total_intra_done_vs_total_intra_ini=[0]*num_mach
                            total_inter_done_vs_total_inter_ini=[0]*num_mach
                            
                            ## cache miss calculation
                            cache_misses_per_machine_top_list=[]
                            ## oct 12
                            removed_node_top_list = [[]for _ in range(num_mach)]
                            removed_max_diff_top_list = [[]for _ in range(num_mach)]
                            fetched_node_top_list = [[]for _ in range(num_mach)]
                            fetch_max_diff_top_list = [[]for _ in range(num_mach)]
                            ##oct 20
                            neighbor_count_top_list=[[]for _ in range(num_mach)]
                            neighbors_top=[[]for _ in range(num_mach)]
                            #oct 20
                            inter_cluster_edge_count_top_list=[[]for _ in range(num_mach)]
                            inter_cluster_top=[[]for _ in range(num_mach)]
                            done_flag=0
                            selected_vert_with_IC_edges_top=[[]for _ in range(num_mach)]
                            ####oct_21
                            change_mode_flag=0
                            ##oct 22
                            no_change=False
                           
                            # file_log=open("simulation_log.txt", "a")
                            ## dec 4
                            ## these keeping tack of edges done per iteration
                            intra_edge_done_top_list=[]
                            inter_edge_done_top_list=[]
                            total_edge_done_top_list=[]
                            
                            ## fixed percentile points
                            booster_percentile_point_75=75 ## first booster gamma
                            booster_percentile_point_90=95 ## second booster gamma point
                            ## fixed ratio intra/total for going intp booster percentile 90
                            gamma_point_2=0.95
                            gamma_point_inter_cluster=0.5 ## jan 22
                            
                            neighbor_count_list_ini=[[]for _ in range(num_mach)]
                            for k in range(num_mach):
                                for element in vert[k]:
                                      neighbor_count_list_ini[k].append(element.total_edges)
                                      #inter_cluster_count[k].append(element.inter_cluster_edge)
                                    ## here were calcuate the percentile
                                print(f'{percentile_point}th degree percentile of machine {k} at iter 0 is: {np.percentile(neighbor_count_list_ini[k], percentile_point)}')
                                sim_log.write(f'{percentile_point}th degree percentile of machine {k} at iter 0 is: {np.percentile(neighbor_count_list_ini[k], percentile_point)}')
                                sim_log.write('\n')
                                gamma[k]=np.percentile(neighbor_count_list_ini[k], percentile_point)
                            
                            trigger_flag=[0]*num_mach
                            print(f'trigger_flag:{trigger_flag}')
                            sim_log.write(f'trigger_flag:{trigger_flag}')
                            sim_log.write('\n')
            
                            on_chip_comm_flag=[0]*num_mach
                            print(f'on_chip_comm_flag:{on_chip_comm_flag}')
                            sim_log.write(f' on_chip_comm_flag:{on_chip_comm_flag}')
                            sim_log.write('\n')
                            
                            inter_cluster_gamma_flag=[0]*num_mach ## jan 22
                            print(f'inter_cluster_gamma_flag:{inter_cluster_gamma_flag}')
                            sim_log.write(f'inter_cluster_gamma_flag:{inter_cluster_gamma_flag}')
                            sim_log.write('\n')
                            ##### setting inter cluster gamma 0 for all machines initially
                            inter_cluster_gamma=[0]*num_mach
                            iter_interval_list_intra=[0]*num_mach
                            iter_interval_list_inter=[0]*num_mach
                          
                            top_computation_cycle_list_per_machine=[]
                            top_mem_stall_cycle_list_per_machine=[]
                            top_PE_utilization_list_per_machine=[]
                            top_num_edges_processed_per_machine=[]
                            
                            num_parts=config_list[0][config_cnt-1]
                            feature_vector_partition_len=math.ceil(hid_1/num_parts)
                            
                            if(feature_vector_partition_len>spad_width):
                              num_PEs_per_edge_pair=math.ceil(feature_vector_partition_len/spad_width)
                            else:
                              num_PEs_per_edge_pair=(feature_vector_partition_len/spad_width) ## computing as a fraction for 32 this will be 0.5
                            
                            # if(feature_vector_partition_len>num_element_processed_per_PE):
                            #   num_PEs_per_edge_pair=math.ceil(feature_vector_partition_len/num_element_processed_per_PE)
                            # else:
                            #   num_PEs_per_edge_pair=(feature_vector_partition_len/num_element_processed_per_PE)
                              
                            num_edge_processed_per_memory_access=math.floor(2*(256/num_PEs_per_edge_pair))
                            
                            if (num_clusters==2):
                                if (num_parts<=5):
                                    packet_latency=5
                                if (num_parts >5 and num_parts<=10):
                                    packet_latency=6
                                if (num_parts>10):
                                     packet_latency=7
                                     
                                     
                            if (num_clusters==4):
                                if (num_parts<=5):
                                    packet_latency=7
                                if (num_parts >5 and num_parts<=10):
                                    packet_latency=8
                                if (num_parts>10):
                                     packet_latency=9
                                     
                            if (num_clusters==8):
                                if (num_parts<=5):
                                    packet_latency=7
                                if (num_parts >5 and num_parts<=10):
                                    packet_latency=9
                                if (num_parts>10):
                                     packet_latency=10
                            
                            if (num_clusters==16):
                                if (num_parts<=5):
                                    packet_latency=10
                                if (num_parts >5 and num_parts<=10):
                                    packet_latency=11
                                if (num_parts>10):
                                     packet_latency=12
                                    
                            print(f'num_parts: {num_parts}')
                            print(f'feature_vector_partition_len : {feature_vector_partition_len}')
                            print(f'num_PEs_per_edge_pair : {num_PEs_per_edge_pair}')
                            print(f'num_edge_processed_per_memory_access : {num_edge_processed_per_memory_access}')
                            
                            sim_log.write(f'num_parts: {num_parts}')
                            sim_log.write('\n')
                            sim_log.write(f'feature_vector_partition_len : {feature_vector_partition_len}')
                            sim_log.write('\n')
                            sim_log.write(f'num_PEs_per_edge_pair : {num_PEs_per_edge_pair}')
                            sim_log.write('\n')
                            sim_log.write(f'num_edge_processed_per_memory_access : {num_edge_processed_per_memory_access}')
                            sim_log.write('\n')
                            
                            ## BEGING VERTEX PROCESSING HERE
                            for iter in range(normal_iter_num):
                                print(f'current GAMMA:{gamma} at ITER:{iter}')
                                sim_log.write(f'current GAMMA:{gamma} at ITER:{iter}')
                                removed_node_cnt  = [0 for _ in range(num_mach)]
                                removed_node_list = [[]for _ in range(num_mach)]
                                # max_diff_list = [[]for _ in range(num_mach)]
                                ### oct 12
                                fetched_node_list=[[]for _ in range(num_mach)]
                                ##oct 20
                                neighbor_count_list=[[]for _ in range(num_mach)]
                                neighbors=[[]for _ in range(num_mach)]
                                ## oct 20
                                inter_cluster_count=[[]for _ in range(num_mach)]
                                inter_cluster_connections=[[]for _ in range(num_mach)]
                                ##
                                list_removed_from_cluster=[[]for _ in range(num_mach)]
                                num_egdes_processed_list=[]
                                num_inter_cluster_edge_processed_list=[]
                                num_intra_cluster_edge_processed_list=[]
                                intra_edge_done_list=[]
                                inter_edge_done_list=[]
                                total_edge_done_list=[]
                                #PE_computation_cycle_list=[]##jan_14
                                computation_cycle_list_per_machine_per_iter=[]
                                #PE utlization calcualtion
                                PE_utilization_per_machine_per_iter=[]
                                # number of edges processed per machine
                                num_edges_processed_per_machine_per_iter=[]
                                
                                cache_miss_cnt_per_machine_per_iter = [0 for _ in range(num_mach)]
                                #global flags
                               
                                
                            
                                for k in range(num_mach):
                                    sub_graph_curr = sub_graph[k]
                                    num_edge_processed=0
                                    num_inter_cluster_edge_processed=0
                                    num_intra_cluster_edge_processed=0
                                    ###FOR CHNAGING GAMMA VALUE #####
                                    ##### BEFORE GRAPH TRAVERSAL #####
                                    # if(iter>=2):
                                    #   #print(f' total node processed:{total_node_processed_per_iter[iter-1][k]} at previous itertion {iter-1}')
                                    #   if(total_node_processed_per_iter[iter-1][k]> (0.9*len(vert[k])) ):
                                    #     print(f"SHOULD CHANGE GAMMA FOR MACHINE: {k}")
                                        # gamma[k]=100
                                        # change_mode_flag=1
                                    ########################################3
                                    ####
                                    removed_nodes=[]## oct_27
                                    for curr_node in sub_graph_curr:
                                        if (curr_node.cluster_id == k):
                                                # continue
                                            for nbr_iter in curr_node.neighbor_list[:]:
                                                # if (curr_node.cluster_id != k):
                                                #     continue
                                                
                                                nbr = vertices[nbr_iter]
                                                if (k in nbr.sub_graph_presence):## ADDED OCT 26
                                                    # entry_1+=1
                                                    if (nbr_iter != curr_node.node_identity):## ADDED OCT 26
                                                        if (curr_node.cluster_id == nbr.cluster_id): ## double count ##
                                                            total_intra_cluster_edges_done_per_machine[k]+=1
                                                            num_intra_cluster_edge_processed+=1
                                                        #     curr_node.inter_cluster_edge_list[curr_node.cluster_id] -=1  
                                                        curr_node.inter_cluster_edge_list[nbr.cluster_id] -=1
                                                            #nbr.total_edges -=1
                                                            #nbr.neighbor_list.remove(curr_node.node_identity)  
                                                        if (curr_node.cluster_id != nbr.cluster_id ):
                                                            nbr.inter_cluster_edge_cnt[1][curr_node.cluster_id] -= 1 ## get commented for two way communication
                                                            # nbr.inter_cluster_edge_list[curr_node.cluster_id] -=1             
                                                            #curr_node.inter_cluster_edge_cnt[0][nbr.cluster_id] -= 1
                                                            #curr_node.inter_cluster_edge_list[nbr.cluster_id] -=1    
                                                            # if(curr_node.inter_cluster_edge_list[nbr.cluster_id]< 0):
                                                            #    #print(" PROBLEM !!!! for curr_node.inter_cluster_edge_list[nbr.cluster_id] ")
                                                            #    sim_log.write(" PROBLEM !!!! for curr_node.inter_cluster_edge_list[nbr.cluster_id] ")
                                                            #nbr.inter_cluster_edge -= 1
                                                            curr_node.inter_cluster_edge -=1 
                                                            total_inter_cluster_edges_done_per_machine[k]+=1
                                                            num_inter_cluster_edge_processed+=1
                                 
                                                    curr_node.total_edges -= 1
                                                    #curr_node.inter_cluster_edge_list[curr_node.cluster_id] -=1    #### added dec_3
                                                    # if(curr_node.inter_cluster_edge_list[curr_node.cluster_id]< 0):
                                                    #    #print(" PROBLEM !!!! for curr_node.inter_cluster_edge_list[curr_node.cluster_id] ")
                                                    #    sim_log.write(" PROBLEM !!!! for curr_node.inter_cluster_edge_list[curr_node.cluster_id] ")
                                                    num_edge_processed+=1
                                                    total_edges_done_per_machine[k]+=1
                                                    # if (curr_node.node_identity==864)and(nbr_iter==359157):
                                                    #     print(f'GOT 359157 NEIGHBOR FOR VERTEX 864 at iter:{iter}')
                                                    #     check_flag_864=1
                                                    # if (curr_node.node_identity==359157)and(nbr_iter==864):
                                                    #     print(f'GOT 864 NEIGHBOR FOR VERTEX 359157 at iter:{iter}')
                                                    #     check_flag_359157=1
                                                    curr_node.neighbor_list.remove(nbr_iter)
                                                else:
                                                    #total_cache_misses_per_machine[k] +=1 ## for tracking the cache misses
                                                    cache_miss_cnt_per_machine_per_iter[k] +=1
                                        
                                        if (inter_cluster_gamma_flag[k]==0):
                                            #print(f'INTER CLUSTER GAMMA FLAG STILL NOT ACTIVATED FOR MACHINE :{k}')
                                            #sim_log.write(f'INTER CLUSTER GAMMA FLAG STILL NOT ACTIVATED FOR MACHINE :{k}')
                                            #sim_log.write('\n')
                                            if curr_node.cluster_id != k and curr_node.inter_cluster_edge_cnt[1][k] == 0 :
                                                removed_node_cnt[k] += 1
                                                # entry_2+=1
                                                #if (k not in curr_node.sub_graph_presence):
                                                  #print(k, curr_node.node_identity, curr_node.sub_graph_presence, curr_node.neighbor_list)
                                                #curr_node.sub_graph_presence.remove(k) ## ADDED OCT 26
                                                #sub_graph_curr.remove(curr_node) ## COMMENTED OCT 27
                                                removed_nodes.append(curr_node)## ADDED OCT 27
                                                removed_node_list[k].append(curr_node.node_identity)
                                                if(k in curr_node.cluster_sent_list):
                                                    #curr_node.cluster_sent_list.remove(k) 
                                                    list_removed_from_cluster[k].append(curr_node.node_identity)
                                        else:
                                              #print(f'!!!!INTER CLUSTER GAMMA FLAG ACTIVATED FOR MACHINE :{k} with:{inter_cluster_gamma[k]} at iter: {iter}')
                                              #sim_log.write(f'!!!!INTER CLUSTER GAMMA FLAG STILL ACTIVATED FOR MACHINE :{k} with: {inter_cluster_gamma[k]} at iter:{iter}')
                                              #sim_log.write('\n')
                                              if curr_node.cluster_id != k and curr_node.inter_cluster_edge_cnt[1][k] <= inter_cluster_gamma[k]:
                                                removed_node_cnt[k] += 1
                                                # entry_2+=1
                                                #if (k not in curr_node.sub_graph_presence):
                                                  #print(k, curr_node.node_identity, curr_node.sub_graph_presence, curr_node.neighbor_list)
                                                #curr_node.sub_graph_presence.remove(k) ## ADDED OCT 26
                                                #sub_graph_curr.remove(curr_node) ## COMMENTED OCT 27
                                                removed_nodes.append(curr_node)## ADDED OCT 27
                                                removed_node_list[k].append(curr_node.node_identity)
                                                if(k in curr_node.cluster_sent_list):
                                                    curr_node.cluster_sent_list.remove(k) 
                                                    list_removed_from_cluster[k].append(curr_node.node_identity)    
                                        if( (curr_node.cluster_id == k) and ( (not curr_node.neighbor_list) or (curr_node.total_edges <= gamma[k]) ) ): 
                                            removed_node_cnt[k] += 1
                                            # entry_3+=1
                                            #if (k not in curr_node.sub_graph_presence):
                                              #print(k, curr_node.node_identity, curr_node.sub_graph_presence, curr_node.neighbor_list)
                                            #curr_node.sub_graph_presence.remove(k) ## ADDED OCT 26
                                            #sub_graph_curr.remove(curr_node) ## commented OCT 27
                                            removed_nodes.append(curr_node)## ADDED OCT 27
                                            removed_node_list[k].append(curr_node.node_identity)
                                            
                                    ## ADDED OCT 27
                                    for curr_node in removed_nodes:
                                        if (k not in curr_node.sub_graph_presence):
                                              print(k, curr_node.node_identity, curr_node.sub_graph_presence, curr_node.neighbor_list)
                                        curr_node.sub_graph_presence.remove(k) ## Addec DEC 8
                                        sub_graph[k].remove(curr_node)
                                        ## need to remove subgraph prresence
                                    ### oct_12
                                    removed_node_top_list[k].append(removed_node_list[k])## oct 12
                                    if(removed_node_list[k]!=[]):
                                          removed_max_diff_top_list[k].append( max(removed_node_list[k]) - min(removed_node_list[k]) )
                                    
                                            
                                    num_egdes_processed_list.append(num_edge_processed)
                                    num_intra_cluster_edge_processed_list.append(num_intra_cluster_edge_processed)
                                    num_inter_cluster_edge_processed_list.append(num_inter_cluster_edge_processed)
                                    num_edges_processed_per_machine_per_iter.append(num_edge_processed)
                                    #print(len(num_egdes_processed_list))
                                    if(iter%1==0):
                                        print("removed from sub_graph ", k, removed_node_cnt[k])
                                        print("num edges processed from sub_graph ", k, num_edge_processed)
                                        print("num intra edges processed from sub_graph ", k, num_intra_cluster_edge_processed)
                                        print("num inter edges processed from sub_graph ", k, num_inter_cluster_edge_processed)
                                        print("cycles required from sub_graph ", k,math.ceil(num_edge_processed/256)) 
                                       
                                        
                                       
            
                                    cycle_count_list[k]+=math.ceil(max(num_egdes_processed_list)/num_edge_processed_per_memory_access*2) ## for cycle counting
                                      ### per machine pe cycle computation ## MULLTIPLICATION BY 2 IS FOR 2 cyckles required to compute 8 elements
                                 
                                    
                                    if removed_node_cnt[k] == 0:
                                      x = [len(c.neighbor_list) for c in sub_graph_curr if c.cluster_id == k]
                                      if x:
                                        mink = min(x)
                                      else:
                                        mink = 0
                                      print(f"min neighbor list size of cluster {k} :", mink, len(sub_graph_curr))
                                    
            
                                
                                           
                                
                                cycle_required_for_PE_computation_per_iter.append(math.ceil(max(num_egdes_processed_list)/num_edge_processed_per_memory_access)*2)
                                
                                ## total edge processed ocuting/tracking
                                top_num_edges_processed_per_machine.append(num_edges_processed_per_machine_per_iter)
                                
                                
                                avaiable_buffer_space_per_iter=[]
                                
                                ## cache miss top count append
                                cache_misses_per_machine_top_list.append(cache_miss_cnt_per_machine_per_iter)
                                
                                ## caluclate the number of refetche here
                                list_refetch_off_chip=[]
                                list_num_refetces_per_iter=[]
                                for k in range(num_mach):
                                      list_num_refetces_per_iter.append(len(sub_graph[k]))
                                      list_refetch_off_chip.append(math.ceil(((len(sub_graph[k])*feature_vector_partition_len)/(307e9/num_clusters))/(.77e-9)))
                                      
                                total_off_chip_cycle_list_refetch.append(list_refetch_off_chip)
                                total_num_refetch_list.append(list_num_refetces_per_iter)
                                cycle_required_for_off_chip_comm_per_iter_refetch.append(max(list_refetch_off_chip))
                                ## compute the blank space
                                for k in range(num_mach):
                                    avaiable_buffer_space_per_iter.append(buffer_cap-len(sub_graph[k]))
        
                                for k in range(num_mach):
                                    computation_cycle_list_per_machine_per_iter.append(math.ceil(num_egdes_processed_list[k]/num_edge_processed_per_memory_access)*16)
                                top_computation_cycle_list_per_machine.append(computation_cycle_list_per_machine_per_iter)
                                
                                for k in range (num_mach):
                                    if (num_edges_processed_per_machine_per_iter[k]/num_edge_processed_per_memory_access)>=1.0:
                                        PE_utilization_per_machine_per_iter.append(1)
                                    else:
                                        PE_utilization_per_machine_per_iter.append(num_edges_processed_per_machine_per_iter[k]/num_edge_processed_per_memory_access)
                                top_PE_utilization_list_per_machine.append(PE_utilization_per_machine_per_iter)
                                
                                for k in range(num_mach):
                                    for element in vert[k]:
                                          neighbor_count_list[k].append(element.total_edges)
                                          inter_cluster_count[k].append(element.inter_cluster_edge)
                                    ## here were calcuate the percentile
                                    print(f'{percentile_point}th degree percentile of machine {k} at iter : {iter} is: {np.percentile(neighbor_count_list[k], percentile_point)}')
                                    sim_log.write(f'{percentile_point}th degree percentile of machine {k} at iter : {iter} is: {np.percentile(neighbor_count_list[k], percentile_point)}')
                                    sim_log.write('\n')
                                    gamma[k]=np.percentile(neighbor_count_list[k], percentile_point)
                                    #### here we calculate the percentile for inter cluster edges
                                    #### here we calculate the percentile for inter cluster edges
                                    print(f'{percentile_point}th degree percentile of inter cluster edges for machine {k} at iter : {iter} is: {np.percentile(inter_cluster_count[k], percentile_point)}')
                                    sim_log.write(f'{percentile_point}th degree percentile of inter cluster edges for machine {k} at iter : {iter} is: {np.percentile(inter_cluster_count[k],percentile_point)}')
                                    sim_log.write('\n')
                                      #### here we calculate the percentile for inter cluster edges
                                    print(f'{percentile_point}th degree percentile of inter cluster edges for machine {k} at iter : {iter} is: {np.percentile(inter_cluster_count[k], 90)}')
                                    sim_log.write(f'{percentile_point}th degree percentile of inter cluster edges for machine {k} at iter : {iter} is: {np.percentile(inter_cluster_count[k],90)}')
                                    sim_log.write('\n')
                                    inter_cluster_gamma[k]=np.percentile(inter_cluster_count[k],90) ## this is fixed currently
                                        
                                    total_done_vs_total_ini[k]=total_edges_done_per_machine[k]/total_intial_edges_per_machine[k]
                                    ## appending it to list
                                    total_edge_done_list.append(total_done_vs_total_ini[k])
                                    print(f'total_done_vs_total_ini of machine {k} at iter : {iter} is: {total_done_vs_total_ini[k]}')
                                    sim_log.write(f'total_done_vs_total_ini of machine {k} at iter : {iter} is: {total_done_vs_total_ini[k]}')
                                    sim_log.write('\n')
                                    print('################################')
                                   
                                    total_intra_done_vs_total_intra_ini[k]=total_intra_cluster_edges_done_per_machine[k]/total_intial_intra_cluster_edges_per_machine[k]
                                    ## appending it to a list
                                    intra_edge_done_list.append(total_intra_done_vs_total_intra_ini[k])
                                    print(f'total_intra_done_vs_total_ini_intra of machine {k} at iter : {iter} is: {total_intra_done_vs_total_intra_ini[k]}')
                                    sim_log.write(f'total_intra_done_vs_total_ini_intra of machine {k} at iter : {iter} is: {total_intra_done_vs_total_intra_ini[k]}')
                                    sim_log.write('\n')
                                    print('################################')
                                    
                                    total_inter_done_vs_total_inter_ini[k]=total_inter_cluster_edges_done_per_machine[k]/total_intial_inter_cluster_edges_per_machine[k]
                                    inter_edge_done_list.append(total_inter_done_vs_total_inter_ini[k])
                                    print(f'total_inter_done_vs_total_ini_inter of machine {k} at iter : {iter} is: {total_inter_done_vs_total_inter_ini[k]}')
                                    sim_log.write(f'total_inter_done_vs_total_ini_inter of machine {k} at iter : {iter} is: {total_inter_done_vs_total_inter_ini[k]}')
                                    sim_log.write('\n')
                                 
                                   
                                    ####
                                 
                                    #### Degree info collection done
                                total_edge_done_top_list.append(total_edge_done_list)
                                intra_edge_done_top_list.append(intra_edge_done_list)
                                inter_edge_done_top_list.append(inter_edge_done_list)
                                ######################################################
                                for k in range (num_mach):
                                    
                                    if(iter>0 and inter_edge_done_top_list[iter-1][k]>0) and (inter_edge_done_top_list[iter][k] <= (1+edge_percent)*inter_edge_done_top_list[iter-1][k] and inter_edge_done_top_list[iter][k]<0.9):
                                          iter_interval_list_inter[k]+=1    
                                   
                                    if(iter_interval_list_inter[k]==iter_iterval):
                                        inter_cluster_gamma_flag[k]=1
                                        print(f'LOW INTER EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write(f'LOW INTER EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write('\n')
                                        iter_interval_list_inter[k]=0 ## reset
                                    else:
                                        inter_cluster_gamma_flag[k]=0
                                        print(f'SUFFICENT INTER EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write(f'SUFFICENT INTER EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write('\n')
                                        
                                 
                                    ### setting the gamma to high percentile due to most of processed edges
                                    if(iter>0 and intra_edge_done_top_list[iter-1][k]>0) and (intra_edge_done_top_list[iter][k] <= (1+edge_percent)*intra_edge_done_top_list[iter-1][k] and  intra_edge_done_top_list[iter][k]<0.9):
                                        iter_interval_list_intra[k]+=1  
                                   
                                    if(iter_interval_list_intra[k]==iter_iterval):
                                        trigger_flag[k]=1
                                        gamma[k]=np.percentile(neighbor_count_list[k], booster_percentile_point_90)
                                        print(f'LOW INTRA EDGE PROCESSED!!ACTIVATING INTRA CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write(f'LOW INTRA EDGE PROCESSED!!ACTIVATING INTRA CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write('\n')
                                        print(f'{booster_percentile_point_90}th degree percentile of machine {k} at iter : {iter} is: {np.percentile(neighbor_count_list[k], booster_percentile_point_90)}')
                                        sim_log.write(f'{booster_percentile_point_90}th degree percentile of machine {k} at iter : {iter} is: {np.percentile(neighbor_count_list[k], booster_percentile_point_90)}')
                                        sim_log.write('\n')
                                        iter_interval_list_intra[k]=0 ## reset
                                    else:
                                        trigger_flag[k]=0
                                        print(f'SUFFICENT INTRA EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write(f'SUFFICENT INTRA EDGE PROCESSED!!ACTIVATING INTER CLUSTER GAMMA!! :{k} at iter: {iter}')
                                        sim_log.write('\n')
                                   
                                     
                            
                                
                                
                                
                                ###############################$############################3    
                                vert_with_inter_cluster_edges=[]
                                count=0
                                ########################################### OFF-CHIP #############
                                list_off_per_iter=[]
                                list_off_cycle_per_iter=[]
                                for k in range(num_mach):
                                    tmpk=dram_index[k]
                                    print(f"Doing off-chip comm communication after on-chip activation for mach {k} with space: {avaiable_buffer_space_per_iter[k]}")
                                    sim_log.write(f"Doing off-chip comm communication after on-chip activation for mach {k} with space: {avaiable_buffer_space_per_iter[k]}")
                                    sim_log.write('\n')
                                    off_chip_access=0
                                    off_chip_cycle_count=0
                                    while  off_chip_access < (off_chip_comm_ratio[k]*avaiable_buffer_space_per_iter[k]): ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                        if (vert[k][tmpk].neighbor_list and k not in vert[k][tmpk].sub_graph_presence):
                                            sub_graph[k].append(vert[k][tmpk]) 
                                            vert[k][tmpk].sub_graph_presence.add(k) ### ADDED oct 26
                                            dram_access_list[k]+=1
                                            off_chip_access+=1
                                        tmpk = (tmpk + 1) % len(vert[k])
                                        if (tmpk == dram_index[k]) or (len(sub_graph[k]) == off_chip_comm_ratio[k]*buffer_cap):
                                            break
                                    dram_index[k] = tmpk
                                    print("num off-chip accesses sub_graph NORMAL mode", k,off_chip_access)
                                    sim_log.write(f'num off-chip accesses sub_graph NORMAL mode is  {k} and {off_chip_access}')
                                    sim_log.write('\n')
                                    print(f"size of sub_graph {k} after off chip : {len(sub_graph[k])}")
                                    sim_log.write(f"size of sub_graph {k} after off chip : {len(sub_graph[k])}")
                                    sim_log.write('\n')
                                    off_chip_cycle_count=(((off_chip_access*feature_vector_partition_len)/(307e9/num_clusters))/(.77e-9))
                                    
                                    list_off_per_iter.append(off_chip_access)
                                    list_off_cycle_per_iter.append(off_chip_cycle_count)
                                    
                                    
                                total_off_chip_comm_list.append(list_off_per_iter)    
                                total_off_chip_cycle_list.append(list_off_cycle_per_iter)
                                cycle_required_for_off_chip_comm_per_iter.append(max(list_off_cycle_per_iter)) ### jan 14
        
                                ##memory stall cycles define here
                                mem_stall_per_machine_per_iter=[]
                                for k in range(num_mach):
                                    if(list_off_cycle_per_iter[k]+list_refetch_off_chip[k]-computation_cycle_list_per_machine_per_iter[k] >0):
                                        mem_stall_per_machine_per_iter.append(list_off_cycle_per_iter[k]+list_refetch_off_chip[k]-computation_cycle_list_per_machine_per_iter[k])
                                    else:
                                        mem_stall_per_machine_per_iter.append(0)
                                top_mem_stall_cycle_list_per_machine.append(mem_stall_per_machine_per_iter)
                                cycle_required_for_mem_stall_per_iter.append(max(mem_stall_per_machine_per_iter)*num_parts)
                                ############################################# ON-CHIP ###########################       
                                list_comm_per_iter_1=[]
                                list_comm_per_iter_2=[]

                                if (num_clusters==64):
                                    list_1,list_2=send_recieve_list(64)
                                ## for 16-machine
                                if (num_clusters==16):
                                    list_1=[0, 2, 4, 6, 8, 10, 12, 14, 0, 1, 4, 5, 8, 9, 12, 13, 0, 1, 4, 5, 8, 9, 12, 13, 0, 1, 2, 3, 8, 9, 10, 11, 0, 1, 2, 3, 8, 9, 10, 11, 0, 1, 2, 3, 8, 9, 10, 11, 0, 1, 2, 3, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7]
            
                                    list_2=[1, 3, 5, 7, 9, 11, 13, 15, 2, 3, 6, 7, 10, 11, 14, 15, 3, 2, 7, 6, 11, 10, 15, 14, 4, 5, 6, 7, 12, 13, 14, 15, 5, 4, 7, 6, 13, 12, 15, 14, 6, 7, 4, 5, 14, 15, 12, 13, 7, 6, 5, 4, 15, 14, 13, 12, 8, 9, 10, 11, 12, 13, 14, 15, 9, 8, 11, 10, 13, 12, 15, 14, 10, 11, 8, 9, 14, 15, 12, 13, 11, 10, 9, 8, 15, 14, 13, 12, 12, 13, 14, 15, 8, 9, 10, 11, 13, 12, 15, 14, 9, 8, 11, 10, 14, 15, 12, 13, 10, 11, 8, 9, 15, 14, 13, 12, 11, 10, 9, 8]
                                if (num_clusters==8):
                                    list_1=[0, 2, 4, 6, 0, 1, 4, 5, 0, 1, 4, 5, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
                                    list_2=[1, 3, 5, 7, 2, 3, 6, 7, 3, 2, 7, 6, 4, 5, 6, 7, 5, 4, 7, 6, 6, 7, 4, 5, 7, 6, 5, 4]
                                ## for 4 machines
                                if (num_clusters==4):
                                    list_1=[0,1,2,0,1,0]
                                    list_2=[1,2,3,2,3,3]
                                    
                                if (num_clusters==2):
                                     list_1=[0]
                                     list_2=[1]
                                
                                on_chip_comm_cycle_count_list_f=[] ## for each pair # num pairs == num mach/2
                                
                                z=[buffer_cap-len(sub_graph[i]) for i in range(num_mach)]
                                if(iter%1==0):
                                    print(f' no of on-chip communication required per machine:{z}')
                                    sim_log.write(f' no of on-chip communication required per machine:{z}')
                                    sim_log.write('\n')
                                    
                                on_chip_comm_traffic_list_f=[]
                                for i in range(len(list_1)):
                                    sent_num=0
                                    for curr_node in sub_graph[list_1[i]]: 
                                        if curr_node.cluster_id == list_2[i]:
                                            continue
                                        ## jan 22 extra constraint
                                        if (inter_cluster_gamma_flag[list_2[i]]==0):
                                            #print(f'INTER CLUSTER GAMMA FLAG NOT ACTIVATED FOR MACHINE :{list_2[i]}')
                                            #sim_log.write(f'INTER CLUSTER GAMMA FLAG NOT ACTIVATED FOR MACHINE :{list_2[i]}')
                                            #sim_log.write('\n')
                                            if (curr_node.inter_cluster_edge_cnt[0][list_2[i]] and  list_2[i] not in curr_node.cluster_sent_list):## add cehck for subgraph presence /sent list
                                                if (len(sub_graph[list_2[i]]) <buffer_cap):  ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                                    sub_graph[list_2[i]].append(curr_node)
                                                    curr_node.sub_graph_presence.add(list_2[i]) ## ADDED OCT 26
                                                    on_chip_comm_list[list_2[i]]+=1
                                                    sent_num += 1
                                                    curr_node.cluster_sent_list.append(list_2[i])
                                        else:
                                
                                              if (curr_node.inter_cluster_edge_cnt[0][list_2[i]] > inter_cluster_gamma[list_2[i]] and  list_2[i] not in curr_node.cluster_sent_list):## add cehck for subgraph presence /sent list
                                                if (len(sub_graph[list_2[i]]) <buffer_cap):  ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                                    sub_graph[list_2[i]].append(curr_node)
                                                    curr_node.sub_graph_presence.add(list_2[i]) ## ADDED OCT 26
                                                    on_chip_comm_list[list_2[i]]+=1
                                                    sent_num += 1
                                                    curr_node.cluster_sent_list.append(list_2[i])
                                                
                                    on_chip_cycle_count= sent_num*packet_latency*num_parts #((sent_num*22)/16e9)/(.77e-9) #sent_num*17*6    ##((sent_num*22)/307e9)/(.77e-9) 
                                    on_chip_comm_traffic_list_f.append(math.ceil(on_chip_cycle_count))
                                    #list_comm_per_iter_1.append(sent_num)    
                                    if(i%(num_clusters/2)==0):
                                        on_chip_comm_cycle_count_list_f.append(max(on_chip_comm_traffic_list_f))
                                        on_chip_comm_traffic_list_f=[]
                                    #print(f"sent {list_1[i]}->{list_2[i]} {sent_num} nodes")
                                    #sim_log.write(f"sent {list_1[i]}->{list_1[i]} {sent_num} nodes")
                                    #sim_log.write('\n')
                                    list_comm_per_iter_1.append(sent_num)
                                  ### swap variables for the folowing
                                on_chip_comm_cycle_count_list_r=[]
                                on_chip_comm_traffic_list_r=[]
                                for i in range(len(list_2)):
                                  sent_num_2=0
                                  for curr_node in sub_graph[list_2[i]]: 
                                        if curr_node.cluster_id == list_1[i]:
                                            continue
                                        if (inter_cluster_gamma_flag[list_1[i]]==0):
                                            #print(f'INTER CLUSTER GAMMA FLAG NOT ACTIVATED FOR MACHINE :{list_1[i]}')
                                            #sim_log.write(f'INTER CLUSTER GAMMA FLAG NOT ACTIVATED FOR MACHINE :{list_1[i]}')
                                            #sim_log.write('\n')
                                            if (curr_node.inter_cluster_edge_cnt[0][list_1[i]] and  list_1[i] not in curr_node.cluster_sent_list):
                                                if (len(sub_graph[list_1[i]]) <buffer_cap):  ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                                    sub_graph[list_1[i]].append(curr_node)
                                                    curr_node.sub_graph_presence.add(list_1[i])## ADDED OCT 26
                                                    on_chip_comm_list[list_1[i]]+=1
                                                    sent_num_2 += 1
                                                    curr_node.cluster_sent_list.append(list_1[i])
                                        else:
                                          
                                            if (curr_node.inter_cluster_edge_cnt[0][list_1[i]] > inter_cluster_gamma[list_1[i]] and  list_1[i] not in curr_node.cluster_sent_list):
                                                if (len(sub_graph[list_1[i]]) <buffer_cap):  ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                                    sub_graph[list_1[i]].append(curr_node)
                                                    curr_node.sub_graph_presence.add(list_1[i])## ADDED OCT 26
                                                    on_chip_comm_list[list_1[i]]+=1
                                                    sent_num_2 += 1
                                                    curr_node.cluster_sent_list.append(list_1[i])
                                  on_chip_cycle_count_2=sent_num_2*packet_latency*num_parts #((sent_num_2*22)/16e9)/(.77e-9)      
                                  on_chip_comm_traffic_list_r.append(math.ceil(on_chip_cycle_count_2))
                                  if(i%(num_clusters/2)==0):
                                        on_chip_comm_cycle_count_list_r.append(max(on_chip_comm_traffic_list_r))
                                        on_chip_comm_traffic_list_r=[]
                                  #print(f"sent {list_2[i]}->{list_1[i]} {sent_num_2} nodes")
                                  #sim_log.write(f"sent {list_2[i]}->{list_1[i]} {sent_num_2} nodes")
                                  #sim_log.write('\n')
                                  list_comm_per_iter_2.append(sent_num_2)
                                  
                                total_on_chip_comm_list_1.append(list_comm_per_iter_1) 
                                total_on_chip_comm_list_2.append(list_comm_per_iter_2) 
                                
                                ## final on-chip communication cycle list
                                #on_chip_comm_cycle_count_list_total=[]
                               
                                if (max(sum(on_chip_comm_cycle_count_list_f),sum(on_chip_comm_cycle_count_list_r))>max(mem_stall_per_machine_per_iter)*num_parts):
                                    cycle_required_for_on_chip_comm_per_iter.append(max(sum(on_chip_comm_cycle_count_list_f),sum(on_chip_comm_cycle_count_list_r))-max(mem_stall_per_machine_per_iter)*num_parts)
                                else:
                                   cycle_required_for_on_chip_comm_per_iter.append(0)
                                ## total on chip commmunication cycle per iteration
                                #cycle_required_for_on_chip_comm_per_iter.append(sum(on_chip_comm_cycle_count_list_total)) ## jan 14
                               
                                for k in range(num_mach):
                                    tmpk=dram_index[k]
                                   
                                    off_chip_access=0
                                    off_chip_cycle_count=0
                                    while (len(sub_graph[k]) < buffer_cap): ## if the buffer is filled or the off-chip comm reaches the desired ratio)
                                        if (vert[k][tmpk].neighbor_list and k not in vert[k][tmpk].sub_graph_presence):
                                            sub_graph[k].append(vert[k][tmpk]) 
                                            vert[k][tmpk].sub_graph_presence.add(k) ### ADDED oct 26
                                            dram_access_list[k]+=1
                                            off_chip_access+=1
                                        tmpk = (tmpk + 1) % len(vert[k])
                                        if (tmpk == dram_index[k]) or (len(sub_graph[k]) == buffer_cap):
                                            break
                                    dram_index[k] = tmpk
                                    
                                    # off_chip_cycle_count=((off_chip_access*128)/307e9)/(.77e-9)
                                    # list_off_per_iter.append(off_chip_access)
                                    # list_off_cycle_per_iter.append(off_chip_cycle_count)
                                    
                                
                                ###################################################################################
                                total_processed_node_list=[]
                                for k in range(num_mach):
                                  count_done = 0
                                  for curr_node in vert[k]:
                                    if (curr_node.total_edges==0):
                                      count_done += 1
                                  #print(f'iter : {iter} k : {k} done : {count_done}')
                                  total_processed_node_list.append(count_done)
                                total_node_processed_per_iter.append(total_processed_node_list)
                                
                                # FOR TWEAKING GAMMA ###############
                           
                                done_count=0
                                for k in range (num_mach):
                                    if ( total_node_processed_per_iter[iter][k] >= 0.8*len(vert[k]) ):
                                        print(f'80 percent node done for machine:{k}')
                                        sim_log.write(f'80 percent node done for machine:{k}')   
                                        sim_log.write('\n')
                                        done_count +=1
                                        if (done_count==num_mach-1):
                                            break
                                
                                
                                if (sum(total_processed_node_list)==len(vertices)):
                                    print(f'All nodes done at iter wihtout the full random access mode at:{iter}')
                                    sim_log.write(f'All nodes done at iter wihtout the full random access mode at:{iter}')
                                    sim_log.write('\n')
                                    break
                            
                            
                            ###### WRITTING OUT DATA #############
                            
                     
                            
                            data = total_edge_done_top_list
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"total_edge_done_top_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/total_egde_done_top_list_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data)
                            
                            data = intra_edge_done_top_list
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"intra_edge_done_top_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/intra_edge_done_top_list_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data)
                            
                            data3 = inter_edge_done_top_list
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"inter_edge_done_top_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/inter_edge_done_top_list_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                                
                            data3 = cache_misses_per_machine_top_list
                              #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"inter_edge_done_top_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/cache_misses_top_list_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                            
                            data = cycle_required_for_PE_computation_per_iter
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"cycle_required_for_PE_computation_per_iter.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/cycle_required_for_PE_computation_per_iter.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
                                
                            data = cycle_required_for_off_chip_comm_per_iter
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"cycle_required_for_off_chip_comm_per_iter.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/cycle_required_for_off_chip_comm_per_iter.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
        
                            data = cycle_required_for_mem_stall_per_iter
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/cycle_required_for_mem_stall_per_iter.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))   
         
                            data = cycle_required_for_on_chip_comm_per_iter
                            #pkl.dump( data, open( "./"+dir_name+"/"+folder_name+"cycle_required_for_on_chip_comm_per_iter.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/cycle_required_for_on_chip_comm_per_iter.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
                            
                            data1 = total_node_processed_per_iter
                            #pkl.dump( data1, open( "./"+dir_name+"/"+folder_name+"total_node_processed_per_iter.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/total_node_processed_per_iter_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data1)
                            
                             
                            data3 = total_on_chip_comm_list_1
                            #pkl.dump( data3, open( "./"+dir_name+"/"+folder_name+"total_on_chip_comm_list_1.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/total_on_chip_comm_list_direct_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                            
                             
                            data3 = total_on_chip_comm_list_2
                            #pkl.dump( data3, open( "./"+dir_name+"/"+folder_name+"total_on_chip_comm_list_2.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"total_on_chip_comm_list_reverse_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                            
                            data3 = top_PE_utilization_list_per_machine
                            #pkl.dump( data3, open( "./"+dir_name+"/"+folder_name+"total_off_chip_comm_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/PE_utilization_per_machine_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                                
                            data3 = top_num_edges_processed_per_machine
                            #pkl.dump( data3, open( "./"+dir_name+"/"+folder_name+"total_off_chip_comm_list.p", "wb" ) )
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Num_edges_processed_per_machine_NORMAL.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(data3)
                            
                            # data3 = total_on_chip_comm_list_2
                            # #pkl.dump( data3, open( "./"+dir_name+"/"+folder_name+"total_on_chip_comm_list_2.p", "wb" ) )
                            # with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"total_on_chip_comm_list_reverse_NORMAL.csv", "w", newline="") as f:
                            #     writer = csv.writer(f)
                            #     writer.writerows(data3)
                            
                            ## followin part is for writing out simulation data
                            gt_5=0
                            incorrect_count_1=0
                            incorrect_count_2=0
                            incorrect_count_3=0
                            for k in range (num_mach):
                                for item in vert[k]:
                                    if (item.total_edges==0):
                                        gt_5+=1
                                        if (np.count_nonzero(item.inter_cluster_edge_list)>0):
                                            incorrect_count_1 +=1
                                            if (item.inter_cluster_edge_list[k]!=0):
                                                incorrect_count_2 +=1
                                    else:
                                        if (np.count_nonzero(item.inter_cluster_edge_list)>0):
                                            for mem in item.inter_cluster_edge_list:
                                                if (mem<0):
                                                  incorrect_count_3 +=1
                            print("gt_5:",gt_5)
                            print("incorrect_count_1:",incorrect_count_1)
                            print("incorrect_count_2:",incorrect_count_2)
                            print("incorrect_count_3:",incorrect_count_3)
                            
                            sim_log.write(f'gt_5:{gt_5}')
                            sim_log.write('\n')
                            
                            print("Total cycle required for PE computation NORMAL:", sum(cycle_required_for_PE_computation_per_iter))
                            # Total_off_chip_cycles= math.ceil(sum(cycle_required_for_off_chip_comm_per_iter) + ((buffer_cap*16)/307e9/num_clusters)/(.77e-9))
                            # print("Total cycle required for off-chip communication NORMAL:", Total_off_chip_cycles)
                            print("Total cycle required for on-chip communication NORMAL:", sum(cycle_required_for_on_chip_comm_per_iter))
                            Total_mem_stall_cycles= math.ceil(sum(cycle_required_for_mem_stall_per_iter) + ((buffer_cap*16)/307e9/num_clusters)/(.77e-9))
                            print("Total cycle required for memory stall NORMAL:", Total_mem_stall_cycles)
                            
                            # Total_cycles_requried_NORMAL=sum(cycle_required_for_PE_computation_per_iter)+Total_off_chip_cycles+sum(cycle_required_for_on_chip_comm_per_iter)
                            # print("Total overall cycles required in NORMAL:",Total_cycles_requried_NORMAL)
                            
                            # Total_cycles_requried_NORMAL_mem_stall=sum(cycle_required_for_PE_computation_per_iter)+Total_mem_stall_cycles+sum(cycle_required_for_on_chip_comm_per_iter)
                            # print("Total overall cycles required in NORMAL mem stall:", Total_cycles_requried_NORMAL_mem_stall)
                            
                            sim_log.write(f"Total cycle required for PE computation NORMAL:{sum(cycle_required_for_PE_computation_per_iter)}")
                            sim_log.write('\n')
                            # sim_log.write(f"Total cycle required for off-chip communication NORMAL: {Total_off_chip_cycles}")
                            # sim_log.write('\n')
                            sim_log.write(f"Total cycle required for on-chip communication NORMAL: {sum(cycle_required_for_on_chip_comm_per_iter)}")
                            sim_log.write('\n')
                            # sim_log.write(f"Total cycle mem stall NORMAL: {Total_mem_stall_cycles}")
                            # sim_log.write('\n')
                            # #Total_cycles_requried_NORMAL=sum(cycle_required_for_PE_computation_per_iter)+sum(cycle_required_for_off_chip_comm_per_iter)+sum(cycle_required_for_on_chip_comm_per_iter)
                            # sim_log.write(f"Total overall cycles required in NORMAL:{Total_cycles_requried_NORMAL}")
                            # sim_log.write('\n')
                            
                            # sim_log.write(f"Total overall cycles required in NORMAL mem stall :{Total_cycles_requried_NORMAL_mem_stall}")
                            # sim_log.write('\n')
                            
                            Normal_PE_cycle_list.append(sum(cycle_required_for_PE_computation_per_iter)) ## Only PE cycles
                            #Normal_off_chip_cycle_list.append(Total_off_chip_cycles)
                            Normal_mem_stall_cycle_list.append(Total_mem_stall_cycles) ## only mem stall cycles
                            Normal_on_chip_cycle_list.append(sum(cycle_required_for_on_chip_comm_per_iter))##only on chip cycles
                            # Normal_total_cycle_list.append(Total_cycles_requried_NORMAL)
                            # Normal_total_cycle_list_mem_stall.append(Total_cycles_requried_NORMAL_mem_stall)
                            
                            data=Normal_PE_cycle_list
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_PE_cycle_list.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
                            
                            # data=Normal_off_chip_cycle_list
                            # with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_off_chip_cycle_list.csv", "w", newline="") as f:
                            #     writer = csv.writer(f)
                            #     writer.writerows(map(lambda x: [x], data))
                                
                            data= Normal_mem_stall_cycle_list
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_mem_stall_cycle_list.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
                            
                            data=Normal_on_chip_cycle_list
                            with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_on_chip_cycle_list.csv", "w", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerows(map(lambda x: [x], data))
                            
                            # data=Normal_total_cycle_list
                            # with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_total_chip_cycle_list.csv", "w", newline="") as f:
                            #     writer = csv.writer(f)
                            #     writer.writerows(map(lambda x: [x], data))
                                
                            # data=Normal_total_cycle_list_mem_stall
                            # with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/"+folder_name+"/Normal_total_cycle_list_mem_stall.csv", "w", newline="") as f:
                            #     writer = csv.writer(f)
                            #     writer.writerows(map(lambda x: [x], data))
                                
                            data_list_per_buffer_and_partitions.append(buffer_cap)
                            data_list_per_buffer_and_partitions.append(num_parts)
                            data_list_per_buffer_and_partitions.append(sum(cycle_required_for_PE_computation_per_iter)+Total_mem_stall_cycles+sum(cycle_required_for_on_chip_comm_per_iter))
                            print(total_edge_done_top_list[-1])
                            data_list_per_buffer_and_partitions.append(sum(total_edge_done_top_list[-1])/len(total_edge_done_top_list[-1]))
                            top_data_list.append(data_list_per_buffer_and_partitions)
                            
    
         
        
        data=top_data_list
        print(data)
        with open("./"+dir_name+"/"+sub_dir_name_1+"/"+sub_dir_name_2+"/top_data.csv", "w", newline="") as f:
             writer = csv.writer(f)
             writer.writerows(data)
    


