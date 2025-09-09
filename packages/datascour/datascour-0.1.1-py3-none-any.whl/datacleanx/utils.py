"""
Utility functions used across the DataCleanX library.
"""
import pandas as pd

def get_numeric_columns(df):
    """
    Identifies and returns the names of numeric columns in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        list: A list of column names that are of a numeric data type.
    """
    return df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()

def get_categorical_columns(df):
    """
    Identifies and returns the names of categorical/object columns in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        list: A list of column names that are of object or category data type.
    """
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

