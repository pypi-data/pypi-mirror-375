"""
Functions for schema, data type validation, and feature scaling/encoding.
"""
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from .utils import get_numeric_columns, get_categorical_columns

def auto_detect_schema(df):
    """
    Automatically detects the schema of a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary representing the detected schema.
    """
    schema = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        if 'int' in dtype:
            schema[col] = 'integer'
        elif 'float' in dtype:
            schema[col] = 'float'
        elif 'bool' in dtype:
            schema[col] = 'boolean'
        elif 'datetime' in dtype:
            schema[col] = 'datetime'
        else:
            schema[col] = 'string'
    return schema

def validate_schema(df, schema, raise_errors=False):
    """
    Validates the DataFrame against a user-defined schema.

    Args:
        df (pd.DataFrame): The input DataFrame.
        schema (dict): The expected schema (e.g., {'col': 'dtype'}).
        raise_errors (bool): If True, raises an error on mismatch.

    Returns:
        tuple: A tuple containing the (potentially corrected) DataFrame and a report dictionary.
    """
    df_copy = df.copy()
    report = {'mismatches': [], 'missing_columns': [], 'extra_columns': []}
    
    schema_cols = set(schema.keys())
    df_cols = set(df_copy.columns)

    report['missing_columns'] = list(schema_cols - df_cols)
    report['extra_columns'] = list(df_cols - schema_cols)

    for col, expected_dtype in schema.items():
        if col not in df_copy.columns:
            continue

        try:
            if expected_dtype == 'integer' and not pd.api.types.is_integer_dtype(df_copy[col]):
                df_copy[col] = pd.to_numeric(df_copy[col], downcast='integer', errors='coerce')
            elif expected_dtype == 'float' and not pd.api.types.is_float_dtype(df_copy[col]):
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
            elif expected_dtype == 'string' and not pd.api.types.is_string_dtype(df_copy[col]):
                 df_copy[col] = df_copy[col].astype(str)
            elif expected_dtype == 'boolean' and not pd.api.types.is_bool_dtype(df_copy[col]):
                 # Handle string representations of booleans
                if df_copy[col].dtype == 'object':
                    df_copy[col] = df_copy[col].astype(str).str.lower().map({'true': True, 'false': False}).fillna(df_copy[col])
                df_copy[col] = df_copy[col].astype(bool)
            elif expected_dtype == 'datetime' and not pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                 df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
            
            # Check if conversion introduced new NaNs
            if df_copy[col].isnull().sum() > df[col].isnull().sum():
                 report['mismatches'].append({'column': col, 'expected': expected_dtype, 'actual': str(df[col].dtype), 'error': 'Conversion failed for some values, resulting in NaN.'})

        except Exception as e:
            msg = f"Column '{col}': Could not convert to {expected_dtype}. Error: {e}"
            if raise_errors: raise TypeError(msg)
            report['mismatches'].append({'column': col, 'expected': expected_dtype, 'actual': str(df[col].dtype), 'error': str(e)})

    return df_copy, report

def scale_numeric_features(df, method='standard'):
    """
    Scales numeric features in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        method (str): The scaling method ('standard' or 'minmax').

    Returns:
        pd.DataFrame: The DataFrame with numeric features scaled.
    """
    df_copy = df.copy()
    numeric_cols = get_numeric_columns(df_copy)

    if not numeric_cols:
        return df_copy

    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError("Unknown scaling method. Use 'standard' or 'minmax'.")

    df_copy[numeric_cols] = scaler.fit_transform(df_copy[numeric_cols])
    return df_copy

def encode_categorical_features(df, method='onehot', drop_first=False):
    """
    Encodes categorical features using One-Hot or Label Encoding.

    Args:
        df (pd.DataFrame): The input DataFrame.
        method (str): The encoding method ('onehot' or 'label').
        drop_first (bool): Whether to drop the first category in one-hot encoding
                           to avoid multicollinearity.

    Returns:
        pd.DataFrame: The DataFrame with categorical features encoded.
    """
    df_copy = df.copy()
    categorical_cols = get_categorical_columns(df_copy)

    if not categorical_cols:
        return df_copy

    # Uniformly cast categorical columns to string to prevent mixed-type errors
    for col in categorical_cols:
        df_copy[col] = df_copy[col].astype(str)

    if method == 'onehot':
        df_copy = pd.get_dummies(df_copy, columns=categorical_cols, drop_first=drop_first, dtype=float)
    elif method == 'label':
        for col in categorical_cols:
            le = LabelEncoder()
            df_copy[col] = le.fit_transform(df_copy[col])
    else:
        raise ValueError("Unknown encoding method. Use 'onehot' or 'label'.")

    return df_copy

