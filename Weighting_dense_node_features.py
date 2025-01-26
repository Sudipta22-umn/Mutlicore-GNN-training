#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 20:17:01 2022

@author: monda089
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 20:24:59 2022

@author: monda089

"""
import math

def weight_cycle_dense_features(data,input_dim, output_dim,num_vertices,buffer_size, num_clusters):
    data=data
    input_layer_dim=input_dim ## 16to match with GNNAdvsior   64 used originally## hidden layer dim
    output_dim=output_dim ## num of class/labels
    PE_array_dim=16 ## 16x16 PE array
    MACs_per_CPE=4
    num_vertices=num_vertices
    input_buffer_size= buffer_size

    num_pass= math.ceil(output_dim/PE_array_dim) # 1
    num_nodes_per_set=math.floor(input_buffer_size/input_layer_dim)#141
    num_set=math.ceil(num_vertices/num_nodes_per_set)#24
    
    sub_vector_len=math.ceil(input_layer_dim/PE_array_dim)
    cycle_required_per_node=math.ceil(sub_vector_len/MACs_per_CPE) #58
    
    total_cycles_required=math.ceil((cycle_required_per_node*num_nodes_per_set*num_pass*num_set)/num_clusters)
    
    return (total_cycles_required,data)

##
#first_layer_weighting_cycles=[]
#second_layer_weighting_cycles=[]
hidden = [64] 	# for GCN
buffer_size=512*1024


dataset = [
# 		('citeseer'	        , 3703	    , 6 ,3327,1   ),  
# 		('cora' 	        	, 1433	    , 7  , 2708, 1),  
# 		('pubmed'	        	, 500	    , 3  ,19717, 2 ),      
# 		('ppi'	            , 50	    , 121 , 56944, 2),   

# 		('PROTEINS_full'             , 29       , 2, 43471, 1) ,   
		('OVCAR-8H'                  , 66       , 2, 1890931,4) , 
		('Yeast'                     , 74       , 2, 1714644,4) ,
		('DD'                        , 89       , 2, 334925,1) ,
		('TWITTER-Real-Graph-Partial', 1323     , 2, 580768,2) ,   
		('SW-620H'                   , 66       , 2, 1889971,4) ,

		( 'amazon0505'               , 96	  , 22, 410236, 4),
		( 'com-amazon'               , 96	  , 22, 548552, 2),
		( 'soc-BlogCatalog'	         , 128    , 39, 88784, 4), 
		( 'amazon0601'  	         , 96	  , 22, 403394,4), 
]




for hid in hidden:
    for data, d, c, num_vertices, num_clusters in dataset:
        # first_layer_weighting_cycles.append(weight_cycle_dense_features(data, d, hid, num_vertices, buffer_size, num_clusters))
        # second_layer_weighting_cycles.append(weight_cycle_dense_features(data, hid, c, num_vertices, buffer_size, num_clusters))
        print(f'Currently processing dataset:{data}')
        ## for type 3 datasets
        first_layer_weighting_cycles=weight_cycle_dense_features(data, d, hid, num_vertices, buffer_size, num_clusters)[0]
        second_layer_weighting_cycles=weight_cycle_dense_features(data, hid, c, num_vertices, buffer_size, num_clusters)[0]

        total_weighting_cycles= first_layer_weighting_cycles + second_layer_weighting_cycles
        print(f'Total weighting cycles for {data} is {total_weighting_cycles}')
        
        
        
        
        
