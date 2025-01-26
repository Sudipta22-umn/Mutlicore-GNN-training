#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 12:12:46 2022

@author: monda089
"""

import os
import shutil
import pickle as pkl
import csv
import math
import copy
import time


class data_processing:
    def __init__(self, name):
        self.name = name
        print("Currently processing dataset:", self.name)

    def create_adj_list(self, name, vertices):
        self.file_name = name
        self.vertices = vertices + 1
        self.cwd = os.getcwd()
        self.adj_list_dir = os.path.join(self.cwd, self.file_name)

        graph_file_path = os.path.join(self.adj_list_dir, f"{self.file_name}_A.txt")
        print(f"Looking for graph file at: {graph_file_path}")
        if not os.path.isfile(graph_file_path):
            print(f"Graph file not found: {graph_file_path}")
            return []

        with open(graph_file_path) as graph_file:
            lines = graph_file.readlines()

        node_alloc_dict = {m: set() for m in range(1, self.vertices)}
        print("Building adjacency list...")
        for line in lines:
            str_1 = line.split(",")
            node_alloc_dict[int(str_1[0])].add(int(str_1[1]))
            node_alloc_dict[int(str_1[1])].add(int(str_1[0]))
        print("Finished building adjacency list.")

        adj_list = [list(neighbors) for neighbors in node_alloc_dict.values()]

        metis_dir = os.path.join(self.adj_list_dir, "METIS")
        if not os.path.exists(metis_dir):
            print("Creating a new METIS directory...")
            os.makedirs(metis_dir)
        else:
            print("METIS directory already exists.")

        output_file = os.path.join(metis_dir, f"{self.file_name}_shifted_by_1.graph")
        print(f"Writing adjacency list to {output_file}")
        with open(output_file, 'w') as file:
            for item in adj_list:
                file.write(" ".join(map(str, item)) + "\n")

        return adj_list


class node_property:
    def __init__(self, neighbor_list, node_identity, total_edges, partition_id,
                 cluster_id, intra_sub_cluster_edge, inter_sub_cluster_edge,
                 inter_cluster_edge, intra_SC_dict={}, inter_SC_dict={},
                 inter_C_dict={}, cluster_sent_list=[]):
        self.neighbor_list = neighbor_list
        self.node_identity = node_identity
        self.total_edges = total_edges
        self.partition_id = partition_id
        self.cluster_id = cluster_id
        self.intra_sub_cluster_edge = intra_sub_cluster_edge
        self.inter_sub_cluster_edge = inter_sub_cluster_edge
        self.inter_cluster_edge = inter_cluster_edge
        self.intra_SC_dict = intra_SC_dict
        self.inter_SC_dict = inter_SC_dict
        self.inter_C_dict = inter_C_dict
        self.cluster_sent_list = cluster_sent_list
        self.sub_graph_presence = list()


def write_csv(filename, data):
    print(f"Writing data to {filename}")
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)


#def num_clusters_required(buffer_size, feature_size, num_vertices):
    #num_feats_per_partition = math.floor(buffer_size / feature_size)
    #thresholds = [0.5, 0.25, 0.125, 0.0625]
    #for i, threshold in enumerate(thresholds, start=1):
        #if num_feats_per_partition >= math.ceil(threshold * num_vertices):
            #print(f"Selected {2 ** (i - 1)} clusters for buffer size {buffer_size}, feature size {feature_size}")
            #return 2 ** (i - 1)
    #print("Selected 16 clusters")
    #return 16


def num_clusters_required(buffer_size,feature_size,num_vertices):
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


def create_node_objects(adj_dict):
    node_obj_dict = {}
    for key, adj_list in adj_dict.items():
        print(f"Creating node objects for dataset: {key}")
        node_object_list = [
            node_property(neighbors, idx + 1, len(neighbors), 0, 0, 0, 0, 0)
            for idx, neighbors in enumerate(adj_list)
        ]
        node_obj_dict[key] = node_object_list
    return node_obj_dict


def calculate_inter_cluster_edges(vertices):
    num_mach = max(v.cluster_id for v in vertices) + 1
    clusters = [[] for _ in range(num_mach)]
    for vertex in vertices:
        clusters[vertex.cluster_id].append(vertex)

    for c in vertices:
        c.inter_cluster_edge_list = [0] * num_mach
        c.inter_cluster_edge = 0
        for nbr in c.neighbor_list:
            nbr_cid = vertices[nbr].cluster_id
            if c.cluster_id != nbr_cid:
                c.inter_cluster_edge_list[nbr_cid] += 1
                c.inter_cluster_edge += 1

    print("Calculated inter-cluster edges.")
    return [[sum(item.inter_cluster_edge_list[i] for item in cluster) for i in range(num_mach)] for cluster in clusters]


def reorder_vertices(vertices):
    print("Reordering vertices based on total edges...")
    prev_id_map = {v.node_identity: idx for idx, v in enumerate(vertices)}
    vertices.sort(key=lambda x: x.total_edges, reverse=True)
    for idx, vertex in enumerate(vertices):
        vertex.node_identity = idx
        vertex.neighbor_list = [prev_id_map[nbr] for nbr in vertex.neighbor_list]
    print("Reordering complete.")
    return vertices


def process_dataset(dataset):
    adj_dict = {}
    for data, _, _, total_vertices in dataset:
        processor = data_processing(data)
        adj_dict[data] = processor.create_adj_list(data, total_vertices + 1)

    node_obj_dict = create_node_objects(adj_dict)

    for data, _, _, total_vertices in dataset:
        num_clusters = min(
            num_clusters_required(512 * 1024, 64, total_vertices),
            num_clusters_required(512 * 1024, 2, total_vertices)
        )

        vertices = node_obj_dict[data]
        print(f"Processing {data} with {num_clusters} clusters.")
        if num_clusters > 1:
            print(f"Loading cluster assignments from {data}_{num_clusters}_clusters.txt")
            with open(f"{data}_{num_clusters}_clusters.txt", "r") as file:
                for count, line in enumerate(file):
                    vertices[count].cluster_id = int(line.split()[0])

        vertices = reorder_vertices(vertices)
        output_file = f"{data}_{'single' if num_clusters == 1 else str(num_clusters)}_ORDERED_METIS.p"
        print(f"Saving ordered vertices to {output_file}")
        pkl.dump(vertices, open(output_file, "wb"))

        inter_cluster_edge_count_top = calculate_inter_cluster_edges(vertices)
        for idx, item in enumerate(inter_cluster_edge_count_top):
            print(f"Cluster {idx}: {item}")


if __name__ == "__main__":
    dataset = [
       

                ('OVCAR-8H'                  , 66       , 2, 1890931) , 
 		('Yeast'                     , 74       , 2, 1714644) ,
		('DD'                        , 89       , 2, 334925) ,
		('TWITTER-Real-Graph-Partial', 1323     , 2, 580768) ,   
 		('SW-620H'                   , 66       , 2, 1889971) ,

    ]
    process_dataset(dataset)

