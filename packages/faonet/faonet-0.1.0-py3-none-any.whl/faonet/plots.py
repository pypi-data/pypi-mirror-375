import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import seaborn as sns

def plot_trade_scatter(df, x_col='Reporter Country Code (M49)', y_col='Partner Country Code (M49)', 
                       value_col='Value', step=10, cmap='viridis', alpha=0.8, figsize=(8, 6)):
    """
    Plot a scatter plot of trade interactions between reporter and partner countries.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing trade data.
    x_col : str
        Column name for x-axis (e.g. reporter country codes).
    y_col : str
        Column name for y-axis (e.g. partner country codes).
    value_col : str
        Column name used for point color intensity (e.g. trade value).
    step : int
        Interval of tick marks on the axes (e.g. show every 10th value).
    cmap : str
        Colormap to use for the scatter points.
    alpha : float
        Transparency level for the points.
    figsize : tuple
        Figure size in inches.

    Returns
    -------
    matplotlib.axes.Axes
        The plot axes object.
    """
    ax = df.plot(kind='scatter', x=x_col, y=y_col, s=32, c=value_col, 
                 cmap=cmap, alpha=alpha, figsize=figsize)

    # Define ticks
    x_ticks = df[x_col].unique()
    y_ticks = df[y_col].unique()
    ax.set_xticks(x_ticks[::step])
    ax.set_yticks(y_ticks[::step])

    # Style
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.show()

    return ax



def plot_bipartite_network2(B, group0_nodes, title=None, figsize=(12, 8), node_size=700, font_size=10):
    """
    Plot a bipartite network using NetworkX with edge weights shown as color intensity.

    Parameters
    ----------
    B : networkx.Graph
        Bipartite graph with 'weight' attributes on edges.
    group0_nodes : list or set
        Nodes from one bipartite group (used for layout positioning).
    title : str, optional
        Title of the plot.
    figsize : tuple
        Figure size in inches.
    node_size : int
        Size of the nodes in the plot.
    font_size : int
        Font size for node labels.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib Axes object of the plot.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Layout
    pos = nx.bipartite_layout(B, group0_nodes)

    # Extract weights
    edges = B.edges(data=True)
    weights = [d['weight'] for (_, _, d) in edges]
    max_weight = max(weights) if weights else 1  # avoid division by zero

    # Draw network
    nx.draw(
        B, pos, ax=ax, with_labels=True, node_size=node_size, font_size=font_size,
        edge_color=weights,
        width=[w / max_weight * 5 for w in weights],
        edge_cmap=plt.cm.Blues
    )

    if title:
        ax.set_title(title)

    plt.tight_layout()
    return ax



def plot_degree_bar(df, country_col="Reporter Country", degree_col="Degree", 
                    title="Node Degree", xlabel="Country", ylabel="Degree", 
                    color="blue", alpha=0.7, figsize=(12, 6), rotation=90):
    """
    Plot a bar chart of node degrees (e.g., exporters or importers) in a bipartite network.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing node information with degree values.
    country_col : str
        Name of the column with country or node names.
    degree_col : str
        Name of the column with degree values.
    title : str
        Title of the plot.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    color : str
        Color used for the bars.
    alpha : float
        Transparency level for the bars (0 to 1).
    figsize : tuple
        Size of the figure in inches (width, height).
    rotation : int
        Rotation angle of the x-axis tick labels.

    Returns
    -------
    matplotlib.axes.Axes
        Axes object of the created plot.
    """
    df_sorted = df.sort_values(by=degree_col, ascending=False)

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(df_sorted[country_col], df_sorted[degree_col], color=color, alpha=alpha)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=rotation)
    plt.tight_layout()
    plt.show()

    return ax


def plot_degree_comparison(df_reporters, df_partners,
                           reporter_country_col="Reporter Country",
                           partner_country_col="Partner Country",
                           degree_col="Degree",
                           figsize=(12, 10),
                           reporter_color="blue",
                           partner_color="orange",
                           alpha=0.7,
                           rotation=90,
                           use_log_scale=False):
    """
    Plot side-by-side scatter plots comparing the degree of reporter and partner countries.

    Parameters
    ----------
    df_reporters : pandas.DataFrame
        DataFrame containing degree values for reporter (exporter) nodes.
    df_partners : pandas.DataFrame
        DataFrame containing degree values for partner (importer) nodes.
    reporter_country_col : str
        Column name for reporter (exporter) country names.
    partner_country_col : str
        Column name for partner (importer) country names.
    degree_col : str
        Column name containing the degree values.
    figsize : tuple
        Size of the entire figure in inches (width, height).
    reporter_color : str
        Color used for the reporter scatter plot.
    partner_color : str
        Color used for the partner scatter plot.
    alpha : float
        Transparency level for the scatter points.
    rotation : int
        Rotation angle for x-axis tick labels.
    use_log_scale : bool
        If True, apply logarithmic scale to the y-axis.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib Figure object containing the two subplots.
    """
    df_reporters_sorted = df_reporters.sort_values(by=degree_col, ascending=False)
    df_partners_sorted = df_partners.sort_values(by=degree_col, ascending=False)

    fig, axs = plt.subplots(1, 2, figsize=figsize, sharey=True)

    axs[0].scatter(df_reporters_sorted[reporter_country_col],
                   df_reporters_sorted[degree_col],
                   color=reporter_color, alpha=alpha)
    axs[0].set_xlabel("Exporter Countries")
    axs[0].set_ylabel("Degree (Number of Connections)")
    axs[0].set_title("Degree - Reporter Countries")
    axs[0].tick_params(axis='x', rotation=rotation)
    if use_log_scale:
        axs[0].set_yscale('log')

    axs[1].scatter(df_partners_sorted[partner_country_col],
                   df_partners_sorted[degree_col],
                   color=partner_color, alpha=alpha)
    axs[1].set_xlabel("Importer Countries")
    axs[1].set_title("Degree - Partner Countries")
    axs[1].tick_params(axis='x', rotation=rotation)
    if use_log_scale:
        axs[1].set_yscale('log')

    plt.tight_layout()
    plt.show()
    return


def plot_degree_by_rank(df_reporters, df_partners,
                        reporter_label="Exporters",
                        partner_label="Importers",
                        degree_col="Degree",
                        figsize=(10, 5),
                        reporter_color="blue",
                        partner_color="orange",
                        alpha=0.7,
                        use_log_y=True,
                        use_log_x=False,
                        title="Node Degree by Rank",
                        xlabel="Rank",
                        ylabel="Degree (Number of Connections)"):
    """
    Plot degree values of reporter and partner countries sorted by rank in descending order.

    Parameters
    ----------
    df_reporters : pandas.DataFrame
        DataFrame containing degree values for reporter (exporter) nodes.
    df_partners : pandas.DataFrame
        DataFrame containing degree values for partner (importer) nodes.
    reporter_label : str
        Label for reporter nodes (used in legend).
    partner_label : str
        Label for partner nodes (used in legend).
    degree_col : str
        Column name containing degree values.
    figsize : tuple
        Size of the figure in inches (width, height).
    reporter_color : str
        Color used for reporter points and fit line.
    partner_color : str
        Color used for partner points and fit line.
    alpha : float
        Transparency level for the scatter points.
    use_log_y : bool
        Whether to use log scale for the y-axis.
    use_log_x : bool
        Whether to use log scale for the x-axis.
    title : str
        Title of the plot.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib Axes object of the plot.
    """
    df_reporters_sorted = df_reporters.sort_values(by=degree_col, ascending=False)
    df_partners_sorted = df_partners.sort_values(by=degree_col, ascending=False)

    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(range(1, len(df_reporters_sorted) + 1),
               df_reporters_sorted[degree_col],
               color=reporter_color,
               label=reporter_label,
               alpha=alpha)

    ax.scatter(range(1, len(df_partners_sorted) + 1),
               df_partners_sorted[degree_col],
               color=partner_color,
               label=partner_label,
               alpha=alpha)

    if use_log_y:
        ax.set_yscale("log")
    if use_log_x:
        ax.set_xscale("log")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()

    return ax


def plot_weight_matrix(df, row="Partner Countries", col="Reporter Countries", 
                       value="Value", cmap="coolwarm", figsize=(20, 15), 
                       title="Weighted Adjacency Matrix (Trade Volume)"):
    """
    Plot a heatmap of the weighted bipartite adjacency matrix.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing filtered trade data with exporter, importer, and weight columns.
    row : str
        Column name to use as rows of the matrix (typically importers).
    col : str
        Column name to use as columns of the matrix (typically exporters).
    value : str
        Column containing the weight or value of the trade relationship.
    cmap : str
        Colormap used for the heatmap.
    figsize : tuple
        Size of the figure in inches (width, height).
    title : str
        Title of the plot.

    Returns
    -------
    matplotlib.axes.Axes
        The Axes object of the resulting heatmap.
    """
    # Build matrix
    matrix = df.pivot(index=row, columns=col, values=value)

    # Sort rows/cols by total weights
    matrix = matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index,
                        matrix.sum(axis=0).sort_values(ascending=False).index]

    # Plot
    plt.figure(figsize=figsize)
    ax = sns.heatmap(matrix, cmap=cmap, annot=False, linewidths=0.5)

    plt.xlabel(col)
    plt.ylabel(row)
    plt.title(title)
    plt.tight_layout()
    plt.show()

    return ax


def plot_top_betweenness(df, col, title=None, color="steelblue", top_n=10, label_col="node", xlabel="Betweenness Centrality"):
    """
    Plot a horizontal bar chart of the top N nodes ranked by betweenness centrality.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing betweenness values and node labels.
    col : str
        Column name containing betweenness centrality scores.
    title : str, optional
        Title of the plot (default is None).
    color : str
        Color of the bars in the chart.
    top_n : int
        Number of top-ranking nodes to display.
    label_col : str
        Column name with node identifiers (default is 'node').
    xlabel : str
        Label for the x-axis.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib Axes object of the plot.
    """
    top = df.sort_values(by=col, ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top[label_col], top[col], color=color)
    ax.set_xlabel(xlabel)
    ax.set_title(title or f"Top {top_n} Nodes by {col}")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

    return ax


def plot_mean_clustering_ratio_vs_degree(df, degree_col="degree", ratio_col="C4_rate", type_col="tipo", node_col="node", show_labels=False):
    """
    Plot the mean clustering ratio ⟨C4b^w / C4b⟩ versus node degree for each node type.

    The function groups nodes by degree and computes the average clustering ratio per group,
    optionally displaying node labels.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least the clustering ratio, node degree, type and identifier columns.
    degree_col : str
        Column name with node degrees.
    ratio_col : str
        Column name with clustering ratio (e.g., C4b^w / C4b).
    type_col : str
        Column name indicating node type (e.g., 'Exportador' or 'Importador').
    node_col : str
        Column name with node identifiers (used for optional annotations).
    show_labels : bool
        Whether to annotate each point with its corresponding node names.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib Axes object of the plot.
    """
    # Group by type and degree
    grouped = (
        df.groupby([type_col, degree_col])
        .agg({
            ratio_col: "mean",
            node_col: lambda x: ', '.join(x)
        })
        .reset_index()
        .rename(columns={node_col: "nodos"})
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each type separately
    for tipo in grouped[type_col].unique():
        subset = grouped[grouped[type_col] == tipo]
        ax.plot(subset[degree_col], subset[ratio_col],
                label=tipo,
                marker='o' if tipo.lower().startswith("export") else 's',
                linestyle='-')

        if show_labels:
            for _, row in subset.iterrows():
                ax.annotate(row["nodos"], (row[degree_col], row[ratio_col]), fontsize=6)

    # Labels and styling
    ax.set_xlabel("Degree")
    ax.set_ylabel("⟨C4b^w / C4b⟩")
    ax.set_title("Mean clustering ratio ⟨C4b^w / C4b⟩ vs. Degree by node type")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    return ax