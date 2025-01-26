#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 00:10:05 2022

@author: monda089
"""

import math
## back propagation time calculation
## the follwoing cycles gets added to the forward calcualtion
def Back_prop_additional(data,num_vertices,num_clusters,hidden_dim_1,hidden_dim_2):
    data=data
    max_vertices_per_cluster=math.ceil(num_vertices/num_clusters)# for amazon 8M dataset
    MACs_per_CPE=4
    PE_array_dim=16*16
    hidden_layer_dim_1=hidden_dim_1 #  64 used earlier; 16 for matching with GNNAdvisor
    hidden_layer_dim_2=hidden_dim_2
    gradient_comp_MAC_ops_1=2*(max_vertices_per_cluster)*hidden_layer_dim_1
    gradient_comp_MAC_ops_2=2*(max_vertices_per_cluster)*hidden_layer_dim_2
    cross_entropy_MAC_ops=(max_vertices_per_cluster)*hidden_layer_dim_2
    Total_additional_MAC_ops=gradient_comp_MAC_ops_1+gradient_comp_MAC_ops_2+cross_entropy_MAC_ops
    Total_additional_cycles=math.ceil(Total_additional_MAC_ops/(MACs_per_CPE*PE_array_dim))
    return (Total_additional_cycles,data)

## first backprop layer

back_prop_additional_cycles_list=[]
hidden = [64] 	
buffer_size=512*1024


dataset = [
# 		('citeseer'	        , 3703	    , 6 ,3327,1   ),  
# 		('cora' 	        	, 1433	    , 7  , 2708, 1),  
# 		('pubmed'	        	, 500	    , 3  ,19717, 2 ),      
# 		('ppi'	            , 50	    , 121 , 56944, 2),   

# 		('PROTEINS_full'             , 29       , 2, 43471, 1) ,   
# 		('OVCAR-8H'                  , 66       , 2, 1890931,4) , 
# 		('Yeast'                     , 74       , 2, 1714644,4) ,
# 		('DD'                        , 89       , 2, 334925,1) ,
# 		('TWITTER-Real-Graph-Partial', 1323     , 2, 580768,2) ,   
# 		('SW-620H'                   , 66       , 2, 1889971,4) ,

		( 'amazon0505'               , 96	  , 22, 410236, 4),
		( 'com-amazon'               , 96	  , 22, 548552, 2),
		( 'soc-BlogCatalog'	         , 128    , 39, 88784, 2), 
		( 'amazon0601'  	         , 96	  , 22, 403394, 4), 
]





for hid in hidden:
    for data, d, c, num_vertices,nc in dataset:
        print(f'Currently processing dataset:{data}')
        back_prop_additional_cycles=Back_prop_additional(data,num_vertices,nc,hid,hid)[0]
        print(f'Additional backpropagation cyles for {data} is {back_prop_additional_cycles}')
     

