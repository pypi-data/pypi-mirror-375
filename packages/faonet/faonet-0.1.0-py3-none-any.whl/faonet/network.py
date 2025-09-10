import networkx as nx

def build_bipartite_network(df, reporter_col, partner_col, weight_col):
    """
    Construct a bipartite network from a FAOSTAT-style trade DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input data containing trade flows.
    reporter_col : str
        Column name for exporter (reporter) countries.
    partner_col : str
        Column name for importer (partner) countries.
    weight_col : str
        Column name for trade volume or weight of the connection.

    Returns
    -------
    B : networkx.Graph
        A bipartite NetworkX graph with edge weights.
    reporters : set
        Set of nodes representing exporters (bipartite=0).
    partners : set
        Set of nodes representing importers (bipartite=1).
    """
    B = nx.Graph()
    reporters = set(df[reporter_col])
    partners = set(df[partner_col])

    B.add_nodes_from(reporters, bipartite=0)
    B.add_nodes_from(partners, bipartite=1)

    for _, row in df.iterrows():
        B.add_edge(row[reporter_col], row[partner_col], weight=row[weight_col])

    return B, reporters, partners

def remove_zero_weight_edges(G):
    """
    Remove all edges with zero weight from a NetworkX graph.

    Parameters
    ----------
    G : networkx.Graph
        The input graph, which must contain a 'weight' attribute on edges.

    Returns
    -------
    G : networkx.Graph
        The modified graph with zero-weight edges removed.
    """
    zero_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("weight", 1) == 0]
    G.remove_edges_from(zero_edges)
    return G
