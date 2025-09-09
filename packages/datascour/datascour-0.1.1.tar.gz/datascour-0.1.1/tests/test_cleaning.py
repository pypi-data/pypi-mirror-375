import pandas as pd
import numpy as np
import pytest
from pandas.testing import assert_frame_equal
from datacleanx import cleaning

# Fixture to create a sample DataFrame for testing
@pytest.fixture
def sample_df():
    data = {
        'A': [1.0, 2.0, np.nan, 4.0, 5.0],
        'B': [10, 20, 30, 40, 500], # Outlier 500
        'C': ['foo', 'bar', 'baz', 'foo', 'qux'],
        'D': [1, 2, 3, 1, 5]
    }
    return pd.DataFrame(data)

# --- Tests for handle_missing ---
def test_handle_missing_mean(sample_df):
    cleaned_df = cleaning.handle_missing(sample_df, strategy='mean')
    assert cleaned_df['A'].isnull().sum() == 0
    assert cleaned_df['A'][2] == pytest.approx((1+2+4+5)/4)

def test_handle_missing_median(sample_df):
    cleaned_df = cleaning.handle_missing(sample_df, strategy='median')
    assert cleaned_df['A'].isnull().sum() == 0
    assert cleaned_df['A'][2] == np.median([1,2,4,5])

def test_handle_missing_mode(sample_df):
    df = pd.DataFrame({'A': [1, 2, 2, np.nan]})
    cleaned_df = cleaning.handle_missing(df, strategy='mode')
    assert cleaned_df['A'][3] == 2

# --- Tests for remove_outliers ---
def test_remove_outliers_iqr(sample_df):
    cleaned_df = cleaning.remove_outliers(sample_df, method='iqr', action='remove', threshold=1.5)
    assert len(cleaned_df) == 4 # Row with outlier 500 should be removed
    assert 500 not in cleaned_df['B'].values

def test_flag_outliers_mad(sample_df):
    # This test now uses the more robust 'mad' method.
    cleaned_df = cleaning.remove_outliers(sample_df, method='mad', action='flag', threshold=3.5)
    assert 'B_is_outlier' in cleaned_df.columns
    assert cleaned_df['B_is_outlier'][4] == True
    assert cleaned_df['B_is_outlier'][0] == False

# --- Tests for remove_duplicates ---
def test_remove_duplicates(sample_df):
    # Add a duplicate row
    df_with_dups = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    assert len(df_with_dups) == 6
    cleaned_df = cleaning.remove_duplicates(df_with_dups)
    assert len(cleaned_df) == 5

# --- Tests for clean_text ---
def test_clean_text():
    text_series = pd.Series(["  Hello World! 123 ", "Another@Example.com", "Testing..."])
    cleaned_series = cleaning.clean_text(text_series, lowercase=True, remove_punct=True, remove_digits=True)
    assert cleaned_series.iloc[0] == "hello world"
    assert cleaned_series.iloc[1] == "anotherexamplecom"
    assert cleaned_series.iloc[2] == "testing"

def test_clean_text_stopwords():
    # Mocking the nltk download
    try:
        import nltk
        nltk.data.find('corpora/stopwords')
    except LookupError:
        pytest.skip("NLTK stopwords not found, skipping test")

    text_series = pd.Series(["this is a sample sentence"])
    cleaned_series = cleaning.clean_text(text_series, remove_stopwords=True)
    assert cleaned_series.iloc[0] == "sample sentence"

# --- Tests for handle_rare_categories ---
def test_handle_rare_categories():
    data = {'city': ['NY', 'NY', 'NY', 'SF', 'SF', 'LA', 'Boston', 'Chicago']}
    df = pd.DataFrame(data)
    # NY: 3/8 (37.5%), SF: 2/8 (25%), LA: 1/8 (12.5%), Boston: 1/8, Chicago: 1/8
    # Threshold 0.15 should group LA, Boston, Chicago
    cleaned_df = cleaning.handle_rare_categories(df, 'city', threshold=0.15, label='Other')
    expected_values = ['NY', 'NY', 'NY', 'SF', 'SF', 'Other', 'Other', 'Other']
    assert cleaned_df['city'].tolist() == expected_values

