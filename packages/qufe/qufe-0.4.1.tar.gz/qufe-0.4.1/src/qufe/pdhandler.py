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


class PandasHandler:
    """
    pandas DataFrame utility handler for data analysis and manipulation.
    
    Provides methods for converting data types, analyzing column structures,
    finding missing data, and data quality validation.
    
    Args:
        default_exclude_cols: Default columns to exclude from NA/empty checks.
                            Can be overridden in individual method calls.
    
    Raises:
        ImportError: If pandas is not installed
    
    Example:
        >>> handler = PandasHandler(default_exclude_cols=['id', 'created_at'])
        >>> result = handler.convert_list_to_tuple_in_df(df)
    """
    
    def __init__(self, default_exclude_cols: Optional[List[str]] = None):
        """Initialize PandasHandler with dependency validation."""
        self.pd = self._import_pandas()
        self.default_exclude_cols = default_exclude_cols or []
    
    def _import_pandas(self):
        """Lazy import pandas with helpful error message."""
        try:
            import pandas as pd
            return pd
        except ImportError as e:
            raise ImportError(
                "Data processing functionality requires pandas. "
                "Install with: pip install qufe[data]"
            ) from e
    
    def _validate_dataframe(self, df) -> None:
        """
        Validate that input is a pandas DataFrame.
        
        Args:
            df: Object to validate
            
        Raises:
            TypeError: If input is not a pandas DataFrame
        """
        if not isinstance(df, self.pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
    
    def help(self) -> None:
        """
        Display help information for pandas DataFrame utilities.

        Shows installation instructions, available methods, and usage examples.
        """
        print("qufe.pdhandler.PandasHandler - pandas DataFrame Utilities")
        print("=" * 60)
        print()
        print("✓ Dependencies: INSTALLED")
        print()
        
        print("AVAILABLE METHODS:")
        print("  • convert_list_to_tuple_in_df(): Convert list values to tuples in DataFrame")
        print("  • show_col_names(): Compare column names across multiple DataFrames")
        print("  • show_all_na(): Extract rows and columns containing NA values")
        print("  • show_all_na_or_empty_rows(): Find rows with NA or empty string values")
        print("  • show_all_na_or_empty_columns(): Find columns with NA or empty string values")
        print()

        print("USAGE EXAMPLES:")
        print("  from qufe.pdhandler import PandasHandler")
        print("  ")
        print("  # Initialize handler")
        print("  handler = PandasHandler(default_exclude_cols=['id'])")
        print("  ")
        print("  # Compare columns across DataFrames")
        print("  col_dict, comparison_df = handler.show_col_names([df1, df2, df3])")
        print("  ")
        print("  # Find all NA values in subset")
        print("  na_subset = handler.show_all_na(df)")
        print("  ")
        print("  # Find problematic rows/columns")
        print("  problem_rows = handler.show_all_na_or_empty_rows(df)")

    def convert_list_to_tuple_in_df(self, df) -> object:
        """
        Convert list values to tuples in DataFrame object columns.

        Preserves None values and other data types unchanged.
        Only processes columns with object dtype that contain list values.

        Args:
            df: Input DataFrame to process (pandas.DataFrame)

        Returns:
            DataFrame with list values converted to tuples

        Raises:
            TypeError: If input is not a pandas DataFrame

        Example:
            >>> handler = PandasHandler()
            >>> df = pd.DataFrame({'col1': [[1, 2], [3, 4]], 'col2': ['a', 'b']})
            >>> result = handler.convert_list_to_tuple_in_df(df)
            >>> print(result['col1'].iloc[0])
            (1, 2)
        """
        self._validate_dataframe(df)
        
        df_copy = df.copy()

        for col in df_copy.columns:
            if df_copy[col].dtype == "object" and df_copy[col].map(type).eq(list).any():
                df_copy[col] = df_copy[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)

        return df_copy

    def show_col_names(self, dfs: List, print_result: bool = False) -> Tuple[Dict[str, List[str]], object]:
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
            TypeError: If input is not a list of DataFrames

        Example:
            >>> handler = PandasHandler()
            >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            >>> df2 = pd.DataFrame({'B': [5, 6], 'C': [7, 8]})
            >>> col_dict, comparison_df = handler.show_col_names([df1, df2])
        """
        if not isinstance(dfs, list) or not all(isinstance(df, self.pd.DataFrame) for df in dfs):
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
        df_check = self.pd.DataFrame(data=df_cols)

        if print_result:
            print(df_check)

        return (df_cols, df_check)

    def show_all_na(self, df) -> object:
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
            TypeError: If input is not a DataFrame

        Example:
            >>> handler = PandasHandler()
            >>> import numpy as np
            >>> df = pd.DataFrame({'A': [1, np.nan], 'B': [3, 4], 'C': [np.nan, 6]})
            >>> na_subset = handler.show_all_na(df)
        """
        self._validate_dataframe(df)

        # Find rows with any NA values
        df_rows_na = df[df.isna().any(axis='columns')]

        # Find columns with any NA values
        df_cols_na = df.columns[df.isna().any()].to_list()

        # Return intersection: rows with NA values, showing only columns with NA values
        df_na = df_rows_na[df_cols_na]

        return df_na

    def show_all_na_or_empty_rows(self, df, exclude_cols: Optional[List[str]] = None) -> object:
        """
        Find rows containing NA values or empty strings.

        Identifies rows that have NA values or empty strings ('') in any column,
        with option to exclude specific columns from the check.

        Args:
            df: Input DataFrame to analyze (pandas.DataFrame)
            exclude_cols: Columns to exclude from NA/empty check. 
                        If None, uses default_exclude_cols from initialization.

        Returns:
            Rows containing NA values or empty strings, with all original columns

        Raises:
            TypeError: If input is not a DataFrame

        Example:
            >>> handler = PandasHandler(default_exclude_cols=['id'])
            >>> df = pd.DataFrame({'A': [1, ''], 'B': [3, 4], 'id': ['x', 'y']})
            >>> problem_rows = handler.show_all_na_or_empty_rows(df)
        """
        self._validate_dataframe(df)

        if exclude_cols is None:
            exclude_cols = self.default_exclude_cols

        # Select columns to check (excluding specified columns)
        cols_to_check = [col for col in df.columns if col not in exclude_cols]
        df_check = df[cols_to_check]

        # Create mask for rows with NA values or empty strings
        mask_row = df_check.isna().any(axis=1) | (df_check == '').any(axis=1)

        # Return complete rows that match the criteria
        df_na_rows = df[mask_row]

        return df_na_rows

    def show_all_na_or_empty_columns(self, df, exclude_cols: Optional[List[str]] = None) -> object:
        """
        Find columns containing NA values or empty strings.

        Identifies columns that have NA values or empty strings ('') in any row,
        with option to exclude specific columns from the check.

        Args:
            df: Input DataFrame to analyze (pandas.DataFrame)
            exclude_cols: Columns to exclude from NA/empty check.
                        If None, uses default_exclude_cols from initialization.

        Returns:
            All rows, but only columns that contain NA values or empty strings

        Raises:
            TypeError: If input is not a DataFrame

        Example:
            >>> handler = PandasHandler(default_exclude_cols=['id'])
            >>> df = pd.DataFrame({'A': [1, 2], 'B': ['', 'x'], 'id': ['y', 'z']})
            >>> problem_cols = handler.show_all_na_or_empty_columns(df)
        """
        self._validate_dataframe(df)

        if exclude_cols is None:
            exclude_cols = self.default_exclude_cols

        # Select columns to check (excluding specified columns)
        cols_to_check = [col for col in df.columns if col not in exclude_cols]

        # Create mask for columns with NA values or empty strings
        mask_col = df[cols_to_check].isna().any(axis=0) | (df[cols_to_check] == '').any(axis=0)

        # Return all rows but only problematic columns
        df_na_cols = df.loc[:, mask_col.index[mask_col]]

        return df_na_cols


# Backward compatibility: provide function-style interface
def help():
    """Display help for PandasHandler (backward compatibility)."""
    try:
        handler = PandasHandler()
        handler.help()
    except ImportError:
        print("qufe.pdhandler - pandas DataFrame Utilities")
        print("=" * 45)
        print()
        print("✗ Dependencies: MISSING")
        print("  Install with: pip install qufe[data]")
        print("  This installs: pandas>=1.1.0, numpy>=1.17.0")
