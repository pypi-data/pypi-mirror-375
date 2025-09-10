import networkx as nx

def export_gml(G, filepath):
    """
    Export a NetworkX graph to a GML file.

    Parameters
    ----------
    G : networkx.Graph
        The graph to be exported.
    filepath : str
        Path to the output .gml file.
    """
    nx.write_gml(G, filepath)
