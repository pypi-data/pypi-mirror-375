import pandas as pd
import numpy as np
import pytest
from pandas.testing import assert_frame_equal
from datacleanx import validation

# Fixture for a sample DataFrame
@pytest.fixture
def validation_df():
    data = {
        'age': ['25', '30', '45'],
        'salary': [50000.0, 60000.5, 75000.2],
        'city': ['New York', 'London', 'Tokyo'],
        'is_manager': [True, 'false', 'True'] # Intentionally mixed types
    }
    return pd.DataFrame(data)

# --- Tests for validate_schema ---
def test_validate_schema_correct_types(validation_df):
    # This test now also implicitly tests boolean conversion logic
    schema = {'age': 'integer', 'is_manager': 'boolean'}
    df_validated, report = validation.validate_schema(validation_df, schema)
    
    assert pd.api.types.is_integer_dtype(df_validated['age'])
    assert pd.api.types.is_bool_dtype(df_validated['is_manager'])
    assert len(report['mismatches']) == 0

def test_validate_schema_mismatch(validation_df):
    # 'age' can be converted, but let's test a column that can't
    df_bad = validation_df.copy()
    df_bad.loc[0, 'age'] = 'twenty-five' # This will cause a coercion error
    
    schema = {'age': 'integer'}
    _, report = validation.validate_schema(df_bad, schema)
    
    assert len(report['mismatches']) > 0
    assert report['mismatches'][0]['column'] == 'age'

def test_validate_schema_missing_and_extra_columns(validation_df):
    schema = {'age': 'integer', 'department': 'string'} # 'department' is missing
    _, report = validation.validate_schema(validation_df, schema)
    
    assert 'department' in report['missing_columns']
    assert 'salary' in report['extra_columns'] # salary is not in schema

# --- Tests for scale_numeric_features ---
def test_scale_numeric_standard(validation_df):
    # First, convert types to be numeric
    df = validation_df.copy()
    df['age'] = pd.to_numeric(df['age'])
    
    scaled_df = validation.scale_numeric_features(df, method='standard')
    
    # Standard scaler should result in a mean close to 0 and std dev close to 1
    assert np.isclose(scaled_df['age'].mean(), 0)
    assert np.isclose(scaled_df['salary'].mean(), 0)
    # CORRECTED: Use ddof=0 for population std dev to match sklearn's calculation
    assert np.isclose(scaled_df['age'].std(ddof=0), 1)
    assert np.isclose(scaled_df['salary'].std(ddof=0), 1)

def test_scale_numeric_minmax(validation_df):
    df = validation_df.copy()
    df['age'] = pd.to_numeric(df['age'])

    scaled_df = validation.scale_numeric_features(df, method='minmax')

    # Min-max scaler should result in values between 0 and 1
    assert np.isclose(scaled_df['age'].min(), 0)
    assert np.isclose(scaled_df['age'].max(), 1)
    assert np.isclose(scaled_df['salary'].min(), 0)
    assert np.isclose(scaled_df['salary'].max(), 1)

# --- Tests for encode_categorical_features ---
def test_encode_categorical_label(validation_df):
    encoded_df = validation.encode_categorical_features(validation_df, method='label')
    
    # Check if categorical columns are now numeric
    assert pd.api.types.is_numeric_dtype(encoded_df['city'])
    assert pd.api.types.is_numeric_dtype(encoded_df['is_manager'])
    assert sorted(encoded_df['city'].unique()) == [0, 1, 2]
    # After casting to string, unique values are 'True' and 'false', which are label encoded
    assert sorted(encoded_df['is_manager'].unique()) == [0, 1]

def test_encode_categorical_onehot(validation_df):
    encoded_df = validation.encode_categorical_features(validation_df, method='onehot')
    
    # Original categorical columns should be gone
    assert 'city' not in encoded_df.columns
    assert 'is_manager' not in encoded_df.columns
    
    # New one-hot encoded columns should exist
    assert 'city_New York' in encoded_df.columns
    assert 'city_London' in encoded_df.columns
    assert 'is_manager_True' in encoded_df.columns
    assert 'is_manager_false' in encoded_df.columns
    
    # Check if the values are correct (e.g., first row is New York and True)
    assert encoded_df['city_New York'][0] == 1.0
    assert encoded_df['city_London'][0] == 0.0
    assert encoded_df['is_manager_True'][0] == 1.0
    assert encoded_df['is_manager_false'][0] == 0.0

