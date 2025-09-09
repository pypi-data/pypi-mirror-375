"""
DataCleanX: An AI-powered Data Cleaning and Validation Toolkit.

This __init__.py file makes the core functions from the different modules
available as a single, cohesive API.
"""
__version__ = "0.1.1"

# Import key functions from modules to expose them at the top-level
from .cleaning import (
    handle_missing,
    remove_outliers,
    remove_duplicates,
    clean_text,
    handle_rare_categories
)

from .validation import (
    validate_schema,
    auto_detect_schema,
    scale_numeric_features,
    encode_categorical_features
)

from .visualization import (
    plot_missing_values,
    generate_report,
    plot_distribution,
    plot_correlation_heatmap,
    plot_outliers
)

def clean(df, 
          missing_strategy='median', 
          outlier_method='mad',  # <-- Updated to the more robust default
          outlier_action='remove',
          validation_schema=None, 
          remove_dups=True):
    """
    A comprehensive one-liner function to clean a DataFrame.

    This function applies a series of common cleaning operations in a logical order.

    Args:
        df (pd.DataFrame): The input DataFrame to clean.
        missing_strategy (str): Strategy for handle_missing(). Defaults to 'median'.
        outlier_method (str): Method for remove_outliers(). Defaults to 'mad'.
        outlier_action (str): Action for remove_outliers(). Defaults to 'remove'.
        validation_schema (dict, optional): Schema for validate_schema(). 
                                            If None, auto-detection is attempted. Defaults to None.
        remove_dups (bool): Whether to remove duplicates. Defaults to True.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    df_clean = df.copy()

    # Step 1: Handle Missing Values
    df_clean = handle_missing(df_clean, strategy=missing_strategy)

    # Step 2: Remove Outliers
    df_clean = remove_outliers(df_clean, method=outlier_method, action=outlier_action)

    # Step 3: Validate and Correct Schema
    if validation_schema:
        df_clean, _ = validate_schema(df_clean, schema=validation_schema)
    else:
        # Auto-detect and apply if no schema is provided
        detected_schema = auto_detect_schema(df_clean)
        df_clean, _ = validate_schema(df_clean, schema=detected_schema)

    # Step 4: Remove Duplicates
    if remove_dups:
        df_clean = remove_duplicates(df_clean)

    print("Data cleaning process complete.")
    return df_clean

