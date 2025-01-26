There are four scripts to count the number of execution cyles required for the Type A datasets.

GAT_aggregation_without_inter_cluster_edges.py --> for GAT.
GCN_aggregation_without_inter_cluster_edges.py --> for GCN.
GINConv_aggregation_without_inter_cluster_edges.py --> for GINConv.
SAGE_aggregation_without_inter_cluster_edges.py --> for GraphSGAE.

The four Type A datasets after preprocessign are saved in pickle format

DD --> DD_single_cluster_ORDERED_METIS.p
OVCAR_8H --> OVCAR_8H_4_clusters_ORDERED.p
SW-620H --> SW-620H_4_clusters.p
TWITTER_Real --> TWIITER_Real-Graph_Patrial_2_clusters.p

To run one the python script please make the following changes:

For instance, for running the script for counting the Aggregation cycles (i.e., GCN_aggregation_without_inter_cluster_edges.py) go to line number 201 and assign the dataset pickle file to the "vertices" variable for which we want to run it for. In addition, also set the values of the following variables to their respective values for a particular datastet:

feature_len --> line 96
num_clusters --> line 97
total_vertices --> line 98

Here feature_len, num_clusters and total_vertices refer to the inout fetaure length, number of clusterers and total number of vertices for a particular dataset under evaluation.









