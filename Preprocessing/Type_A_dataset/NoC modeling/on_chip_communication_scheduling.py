#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 18:06:01 2022

@author: monda089
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 01:20:38 2022

@author: sudiptamondal
"""

# from itertools import combinations
  
# letters ='01234567'
# #numbers=[2,3,5,6]
  
# # size of combination is set to 3
# a = combinations(letters, 2) 
# y = [' '.join(i) for i in a]
# print(y)

# # b=combinations(numbers, 2)
# # print(b)

# comb_list=[]
# send_list=[]
# recieve_list=[]

# for item in y:
#     list_1=[]
#     list_1.append(int(item[0]))
#     send_list.append(int(item[0]))
#     list_1.append(int(item[2]))
#     recieve_list.append(int(item[2]))
#     comb_list.append(list_1)
#     list_1=[]




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

sending_machines_list, recieving_machines_list= send_recieve_list(64)