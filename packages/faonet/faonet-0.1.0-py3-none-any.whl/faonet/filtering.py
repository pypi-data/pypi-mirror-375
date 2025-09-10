def filter_top_percentile(df, value_column="Value", percentile=0.9):
    """
    Filter a DataFrame to retain rows that account for a given cumulative percentile of a value column.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to be filtered.
    value_column : str
        Column name to use for cumulative sum and filtering (e.g., trade value).
    percentile : float
        Cumulative threshold to retain (between 0 and 1, e.g., 0.9 for top 90%).

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only the rows that fall within the specified cumulative percentile.

    """
    df_sorted = df.sort_values(by=value_column, ascending=False)
    total_value = df_sorted[value_column].sum()
    df_sorted["cumsum"] = df_sorted[value_column].cumsum()
    df_sorted["cumperc"] = df_sorted["cumsum"] / total_value
    return df_sorted[df_sorted["cumperc"] <= percentile].copy()
