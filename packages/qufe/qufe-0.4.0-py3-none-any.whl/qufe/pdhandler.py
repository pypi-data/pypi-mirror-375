"""
pandas DataFrame utility functions for data analysis and manipulation.

This module provides utilities for:
- Converting data types within DataFrames
- Analyzing column structures across multiple DataFrames
- Finding and extracting rows/columns with missing or empty data
- Data quality validation and exploration

Required dependencies:
    pip install qufe[data]

This installs: pandas>=1.1.0, numpy>=1.17.0
"""

from typing import List, Tuple, Dict, Any, Optional, Union


# Lazy import for pandas
def _import_pandas():
    """Lazy import pandas with helpful error message."""
    try:
        import pandas as pd
        return pd
    except ImportError as e:
        raise ImportError(
            "Data processing functionality requires pandas. "
            "Install with: pip install qufe[data]"
        ) from e


def help():
    """
    Display help information for pandas DataFrame utilities.

    Shows installation instructions, available functions, and usage examples.
    """
    print("qufe.pdhandler - pandas DataFrame Utilities")
    print("=" * 45)
    print()

    try:
        _import_pandas()
        print("✓ Dependencies: INSTALLED")
    except ImportError:
        print("✗ Dependencies: MISSING")
        print("  Install with: pip install qufe[data]")
        print("  This installs: pandas>=1.1.0, numpy>=1.17.0")
        print()
        return

    print()
    print("AVAILABLE FUNCTIONS:")
    print("  • convert_list_to_tuple_in_df(): Convert list values to tuples in DataFrame")
    print("  • show_col_names(): Compare column names across multiple DataFrames")
    print("  • show_all_na(): Extract rows and columns containing NA values")
    print("  • show_all_na_or_empty_rows(): Find rows with NA or empty string values")
    print("  • show_all_na_or_empty_columns(): Find columns with NA or empty string values")
    print()

    print("USAGE EXAMPLES:")
    print("  from qufe.pdhandler import show_col_names, show_all_na")
    print("  ")
    print("  # Compare columns across DataFrames")
    print("  col_dict, comparison_df = show_col_names([df1, df2, df3])")
    print("  ")
    print("  # Find all NA values in subset")
    print("  na_subset = show_all_na(df)")
    print("  ")
    print("  # Find problematic rows/columns")
    print("  problem_rows = show_all_na_or_empty_rows(df, exclude_cols=['id'])")


def convert_list_to_tuple_in_df(df) -> object:
    """
    Convert list values to tuples in DataFrame object columns.

    Preserves None values and other data types unchanged.
    Only processes columns with object dtype that contain list values.

    Args:
        df: Input DataFrame to process (pandas.DataFrame)

    Returns:
        DataFrame with list values converted to tuples

    Raises:
        ImportError: If pandas is not installed

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [[1, 2], [3, 4]], 'col2': ['a', 'b']})
        >>> result = convert_list_to_tuple_in_df(df)
        >>> print(result['col1'].iloc[0])
        (1, 2)
    """
    pd = _import_pandas()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    df_copy = df.copy()

    for col in df_copy.columns:
        if df_copy[col].dtype == "object" and df_copy[col].map(type).eq(list).any():
            df_copy[col] = df_copy[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)

    return df_copy


def show_col_names(dfs: List, print_result: bool = False) -> Tuple[Dict[str, List[str]], object]:
    """
    Compare column names across multiple DataFrames.

    Creates a comprehensive view of all columns present in the input DataFrames,
    showing which columns exist in each DataFrame.

    Args:
        dfs: List of DataFrames to compare (List[pandas.DataFrame])
        print_result: Whether to print the comparison table. Defaults to False.

    Returns:
        Tuple containing:
        - Dictionary mapping DataFrame names to column lists
        - Comparison DataFrame showing column presence across DataFrames

    Raises:
        ImportError: If pandas is not installed
        TypeError: If input is not a list of DataFrames

    Example:
        >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> df2 = pd.DataFrame({'B': [5, 6], 'C': [7, 8]})
        >>> col_dict, comparison_df = show_col_names([df1, df2])
    """
    pd = _import_pandas()

    if not isinstance(dfs, list) or not all(isinstance(df, pd.DataFrame) for df in dfs):
        raise TypeError("Input must be a list of pandas DataFrames")

    # Create dictionary mapping each DataFrame to its column list
    all_df = {f'df_{idx + 1}': df.columns.to_list() for (idx, df) in enumerate(dfs)}

    # Get all unique column names across all DataFrames
    all_cols = list(set(col for df_cols in all_df.values() for col in df_cols))
    all_cols = sorted(all_cols)

    # Create comparison dictionary
    df_cols = {'All': all_cols}
    df_cols.update({
        df_name: [col if col in df_columns else '' for col in all_cols]
        for (df_name, df_columns) in all_df.items()
    })

    # Convert to DataFrame for easy viewing
    df_check = pd.DataFrame(data=df_cols)

    if print_result:
        print(df_check)

    return (df_cols, df_check)


def show_all_na(df) -> object:
    """
    Extract rows and columns that contain NA values.

    Returns a subset of the original DataFrame containing only:
    - Rows that have at least one NA value
    - Columns that have at least one NA value

    Args:
        df: Input DataFrame to analyze (pandas.DataFrame)

    Returns:
        Subset containing only rows and columns with NA values

    Raises:
        ImportError: If pandas is not installed
        TypeError: If input is not a DataFrame

    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'A': [1, np.nan], 'B': [3, 4], 'C': [np.nan, 6]})
        >>> na_subset = show_all_na(df)
    """
    pd = _import_pandas()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    # Find rows with any NA values
    df_rows_na = df[df.isna().any(axis='columns')]

    # Find columns with any NA values
    df_cols_na = df.columns[df.isna().any()].to_list()

    # Return intersection: rows with NA values, showing only columns with NA values
    df_na = df_rows_na[df_cols_na]

    return df_na


def show_all_na_or_empty_rows(df, exclude_cols: Optional[List[str]] = None) -> object:
    """
    Find rows containing NA values or empty strings.

    Identifies rows that have NA values or empty strings ('') in any column,
    with option to exclude specific columns from the check.

    Args:
        df: Input DataFrame to analyze (pandas.DataFrame)
        exclude_cols: Columns to exclude from NA/empty check. Defaults to None.

    Returns:
        Rows containing NA values or empty strings, with all original columns

    Raises:
        ImportError: If pandas is not installed
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, ''], 'B': [3, 4], 'C': ['x', 'y']})
        >>> problem_rows = show_all_na_or_empty_rows(df, exclude_cols=['C'])
    """
    pd = _import_pandas()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if exclude_cols is None:
        exclude_cols = []

    # Select columns to check (excluding specified columns)
    cols_to_check = [col for col in df.columns if col not in exclude_cols]
    df_check = df[cols_to_check]

    # Create mask for rows with NA values or empty strings
    mask_row = df_check.isna().any(axis=1) | (df_check == '').any(axis=1)

    # Return complete rows that match the criteria
    df_na_rows = df[mask_row]

    return df_na_rows


def show_all_na_or_empty_columns(df, exclude_cols: Optional[List[str]] = None) -> object:
    """
    Find columns containing NA values or empty strings.

    Identifies columns that have NA values or empty strings ('') in any row,
    with option to exclude specific columns from the check.

    Args:
        df: Input DataFrame to analyze (pandas.DataFrame)
        exclude_cols: Columns to exclude from NA/empty check. Defaults to None.

    Returns:
        All rows, but only columns that contain NA values or empty strings

    Raises:
        ImportError: If pandas is not installed
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': ['', 'x'], 'C': ['y', 'z']})
        >>> problem_cols = show_all_na_or_empty_columns(df, exclude_cols=['C'])
    """
    pd = _import_pandas()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if exclude_cols is None:
        exclude_cols = []

    # Select columns to check (excluding specified columns)
    cols_to_check = [col for col in df.columns if col not in exclude_cols]

    # Create mask for columns with NA values or empty strings
    mask_col = df[cols_to_check].isna().any(axis=0) | (df[cols_to_check] == '').any(axis=0)

    # Return all rows but only problematic columns
    df_na_cols = df.loc[:, mask_col.index[mask_col]]

    return df_na_cols
