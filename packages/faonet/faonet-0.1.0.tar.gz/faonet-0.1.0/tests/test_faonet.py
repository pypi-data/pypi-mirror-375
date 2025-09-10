
import pytest
import pandas as pd
import networkx as nx
from faonet.metrics import compute_degree_and_strength
from faonet.network import build_bipartite_network
from faonet.metrics import compute_bipartite_clustering

def test_build_graph_and_compute_metrics():
    data = {
        'Reporter Countries': ['A', 'A', 'B', 'C'],
        'Partner Countries': ['X', 'Y', 'Y', 'Z'],
        'Value': [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)
    B, reporters, partners = build_bipartite_network(df, 'Reporter Countries', 'Partner Countries', 'Value')
    df_exporters, df_importers = compute_degree_and_strength(B, reporters, partners)

    assert "Degree" in df_exporters.columns
    assert "Strength" in df_exporters.columns
    assert len(df_exporters) == len(reporters)

def test_clustering_does_not_fail():
    B = nx.Graph()
    B.add_edge('A', 'X', weight=1)
    B.add_edge('A', 'Y', weight=1)
    B.add_edge('B', 'X', weight=1)
    B.add_edge('B', 'Y', weight=1)
    df_clust = compute_bipartite_clustering(B)
    assert "C4b" in df_clust.columns
    assert "C4b^w" in df_clust.columns
