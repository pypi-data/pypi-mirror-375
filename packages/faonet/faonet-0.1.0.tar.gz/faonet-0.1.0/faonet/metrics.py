import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
import itertools
import numpy as np

def degree_by_group(G, group_nodes):
    """
    Compute the degree (number of connections) for a given group of nodes.

    Parameters
    ----------
    G : networkx.Graph
        The network graph.
    group_nodes : iterable
        Set or list of nodes for which to compute the degree.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['Node', 'Degree'].
    """
    degrees = {n: G.degree(n) for n in group_nodes}
    return pd.DataFrame(degrees.items(), columns=["Node", "Degree"])



def compute_degree_and_strength(B, reporters, partners):
    """
    Compute the degree and strength (sum of edge weights) for nodes in a bipartite network.

    Parameters
    ----------
    B : networkx.Graph
        Bipartite graph with weights on the edges (under the 'weight' attribute).
    reporters : set
        Set of nodes in one bipartite group (e.g., exporters).
    partners : set
        Set of nodes in the other bipartite group (e.g., importers).

    Returns
    -------
    tuple of pd.DataFrame
        (df_exporters, df_importers):
        - df_exporters : DataFrame with 'Degree' and 'Strength' for reporter nodes.
        - df_importers : DataFrame with 'Degree' and 'Strength' for partner nodes.
    
    Compute degree and strength (sum of weights) for nodes in a bipartite network.
    """
    # Compute strength: sum of edge weights per node
    strength = {
        node: sum(data['weight'] for _, _, data in B.edges(node, data=True))
        for node in B.nodes()
    }

    # Compute degree using built-in function
    degree = dict(B.degree())

    # Separate by node group
    exporters_strength = {node: strength[node] for node in reporters}
    importers_strength = {node: strength[node] for node in partners}
    exporters_degree = {node: degree[node] for node in reporters}
    importers_degree = {node: degree[node] for node in partners}

    # Create dataframes
    df_exporters = pd.DataFrame({
        "Degree": pd.Series(exporters_degree),
        "Strength": pd.Series(exporters_strength)
    }).dropna()

    df_importers = pd.DataFrame({
        "Degree": pd.Series(importers_degree),
        "Strength": pd.Series(importers_strength)
    }).dropna()

    return df_exporters, df_importers



def compute_betweenness_all(G):
    """
    Compute multiple betweenness centrality measures for a bipartite network.

    This function calculates:
    - Betweenness in the full bipartite network using both real and inverted weights.
    - Betweenness in the projected graphs (for exporters and importers), again with real and inverted weights.

    Parameters
    ----------
    G : networkx.Graph
        Bipartite graph with edge attribute 'weight'.

    Returns
    -------
    pd.DataFrame
        DataFrame with one row per node and the following columns:
        - 'node': Node identifier
        - 'bipartite_set': 0 if exporter, 1 if importer
        - 'betweenness_bipartite': Centrality in full bipartite graph (weights)
        - 'betweenness_bipartite_inv': Centrality in full bipartite graph (inverted weights)
        - 'betweenness_proj_exporters': Centrality in exporter projection (weights)
        - 'betweenness_proj_exporters_inv': Centrality in exporter projection (inverted weights)
        - 'betweenness_proj_importers': Centrality in importer projection (weights)
        - 'betweenness_proj_importers_inv': Centrality in importer projection (inverted weights)
    """
    # Identify bipartite sets
    exportadores = {n for n, d in G.nodes(data=True) if d.get("bipartite") == 0}
    importadores = set(G) - exportadores

    # Invert weights for shortest-path based betweenness
    G_inv = G.copy()
    for u, v, d in G_inv.edges(data=True):
        peso = d.get("weight", 1)
        d["inv_weight"] = 1 / peso if peso > 0 else 0

    # Betweenness in original bipartite network
    bet_bip = nx.betweenness_centrality(G, weight="weight")
    bet_bip_inv = nx.betweenness_centrality(G_inv, weight="inv_weight")

    # Projected graphs
    proy_exp = bipartite.weighted_projected_graph(G, exportadores)
    proy_imp = bipartite.weighted_projected_graph(G, importadores)

    # Betweenness in projections (real weights)
    bet_proy_exp = nx.betweenness_centrality(proy_exp, weight="weight")
    bet_proy_imp = nx.betweenness_centrality(proy_imp, weight="weight")

    # Invert weights in projections
    for _, _, d in proy_exp.edges(data=True):
        d["inv_weight"] = 1 / d["weight"] if d["weight"] > 0 else 0
    for _, _, d in proy_imp.edges(data=True):
        d["inv_weight"] = 1 / d["weight"] if d["weight"] > 0 else 0

    bet_proy_exp_inv = nx.betweenness_centrality(proy_exp, weight="inv_weight")
    bet_proy_imp_inv = nx.betweenness_centrality(proy_imp, weight="inv_weight")

    # Build results
    nodos = list(G.nodes())
    df_bet = pd.DataFrame({
        "node": nodos,
        "bipartite_set": [G.nodes[n].get("bipartite") for n in nodos],
        "betweenness_bipartite": [bet_bip.get(n, 0) for n in nodos],
        "betweenness_bipartite_inv": [bet_bip_inv.get(n, 0) for n in nodos],
        "betweenness_proj_exporters": [bet_proy_exp.get(n, None) for n in nodos],
        "betweenness_proj_exporters_inv": [bet_proy_exp_inv.get(n, None) for n in nodos],
        "betweenness_proj_importers": [bet_proy_imp.get(n, None) for n in nodos],
        "betweenness_proj_importers_inv": [bet_proy_imp_inv.get(n, None) for n in nodos],
    })

    return df_bet


def compute_bipartite_clustering(G, reporters=None, normalized=True):
    """
    Compute bipartite clustering coefficients C4b and C4b^w for each node in a bipartite graph.

    Parameters
    ----------
    G : networkx.Graph
        Bipartite graph with edge attribute 'weight'.
        reporters (set, optional): Set of nodes considered "Exportadores". 
                                   All others will be labeled "Importadores" if this is provided.
        normalized (bool): Whether to use normalized version of the clustering.

    Returns
    -------
    pd.DataFrame: 
        DataFrame with C4b, C4b^w, their ratio, degree and type.
    """

    def c4b_node(G, node):
        neighbors = list(G[node])
        k_i = len(neighbors)
        s_i = sum(G[node][n].get("weight", 1) for n in neighbors)

        if k_i < 2:
            return 0.0, 0.0

        neighbor_pairs = list(itertools.combinations(neighbors, 2))
        q_i = 0
        qw_i = 0.0

        for m, n in neighbor_pairs:
            neighbors_m = set(G[m])
            neighbors_n = set(G[n])
            common = neighbors_m & neighbors_n - {node}

            for v in common:
                q_i += 1
                w_im = G[node][m].get("weight", 1)
                w_in = G[node][n].get("weight", 1)
                wnorm_m = w_im / s_i if s_i > 0 else 0
                wnorm_n = w_in / s_i if s_i > 0 else 0
                qw_i += (wnorm_m + wnorm_n) / 2

        # Normalization term
        k_nn = len(set.union(*(set(G[n]) for n in neighbors)) - {node})
        Q_i = k_i * (k_i - 1) / 2 * k_nn if normalized else 1

        C4b = q_i / Q_i if Q_i > 0 else 0
        C4bw = qw_i / Q_i if Q_i > 0 else 0
        return C4b, C4bw

    # Compute clustering for all nodes
    results = []
    for node in G.nodes():
        c4b, c4bw = c4b_node(G, node)
        results.append({
            "node": node,
            "C4b": c4b,
            "C4b^w": c4bw,
            "degree": G.degree(node)
        })

    df = pd.DataFrame(results)
    df["C4_rate"] = df["C4b^w"] / df["C4b"]
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    if reporters is not None:
        df["tipo"] = df["node"].apply(lambda x: "Exportador" if x in reporters else "Importador")

    return df