import pandas as pd

def load_and_merge_csv(filepaths):
    """
    Load and concatenate multiple FAOSTAT CSV files into a single DataFrame.

    Parameters
    ----------
    filepaths : list of str
        List of paths to the CSV files.

    Returns
    -------
    pd.DataFrame
        A single DataFrame resulting from concatenation of all input files.
    """

    dataframes = [pd.read_csv(path) for path in filepaths]
    return pd.concat(dataframes, ignore_index=True)

def load_file(file, year=2023):
    """
    Load a single FAOSTAT CSV file and filter by a specific year.

    Parameters
    ----------
    file : str or path-like
        Path to the CSV file.
    year : int, optional
        Year to filter the data by (default is 2023).

    Returns
    -------
    pd.DataFrame
        DataFrame filtered to only include data from the specified year.
    """

    dataframes = pd.read_csv(file)
    return dataframes[dataframes['Year'] == year]


def save_dataframe(df, filepath):
    """
    Save a pandas DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    filepath : str
        Destination path for the output CSV file.
    """
    df.to_csv(filepath, index=False)
