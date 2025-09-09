"""
Core data cleaning functions for handling missing values, outliers, and duplicates.
"""
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest
from .utils import get_numeric_columns, get_categorical_columns
import re
import string
import nltk

def _ensure_nltk_data(data_name):
    """Helper function to download NLTK data if not present."""
    try:
        nltk.data.find(f'corpora/{data_name}')
    except LookupError:
        print(f"NLTK data '{data_name}' not found. Downloading...")
        nltk.download(data_name, quiet=True)

def handle_missing(df, strategy='mean', **kwargs):
    """
    Handles missing values in a DataFrame using various strategies.
    """
    df_copy = df.copy()
    numeric_cols = get_numeric_columns(df_copy)
    
    if strategy in ['mean', 'median']:
        for col in numeric_cols:
            if df_copy[col].isnull().sum() > 0:
                impute_value = df_copy[col].mean() if strategy == 'mean' else df_copy[col].median()
                # Use .loc for safe assignment to avoid warnings
                df_copy.loc[df_copy[col].isnull(), col] = impute_value
    elif strategy == 'mode':
        for col in df_copy.columns:
             if df_copy[col].isnull().sum() > 0:
                impute_value = df_copy[col].mode()[0]
                # Use .loc for safe assignment to avoid warnings
                df_copy.loc[df_copy[col].isnull(), col] = impute_value
    elif strategy == 'knn':
        n_neighbors = kwargs.get('n_neighbors', 5)
        imputer = KNNImputer(n_neighbors=n_neighbors)
        if numeric_cols:
            df_copy[numeric_cols] = imputer.fit_transform(df_copy[numeric_cols])
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return df_copy

def remove_outliers(df, method='mad', threshold=3.5, action='remove'):
    """
    Detects and handles outliers in the numeric columns of a DataFrame.
    """
    df_copy = df.copy()
    numeric_cols = get_numeric_columns(df_copy)
    
    overall_outlier_indices = pd.Series([False] * len(df_copy), index=df_copy.index)

    for col in numeric_cols:
        col_outliers = pd.Series([False] * len(df_copy), index=df_copy.index)
        
        if method == 'iqr':
            Q1 = df_copy[col].quantile(0.25)
            Q3 = df_copy[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            col_outliers = (df_copy[col] < lower_bound) | (df_copy[col] > upper_bound)
        elif method == 'mad':
            median = df_copy[col].median()
            mad = np.median(np.abs(df_copy[col].dropna() - median))
            if mad > 0:
                modified_z_scores = 0.6745 * (df_copy[col] - median) / mad
                col_outliers = np.abs(modified_z_scores) > threshold
        else:
            raise ValueError(f"Unknown method: {method}. Options are 'iqr' or 'mad'.")
        
        if action == 'flag':
            df_copy[f'{col}_is_outlier'] = col_outliers.fillna(False)
        
        overall_outlier_indices = overall_outlier_indices | col_outliers

    if action == 'remove':
        return df_copy[~overall_outlier_indices]
    elif action == 'flag':
        return df_copy
    else:
        raise ValueError(f"Unknown action: {action}. Options are 'remove' or 'flag'.")

def remove_duplicates(df, subset=None, keep='first'):
    """
    Removes duplicate rows from a DataFrame.
    """
    return df.drop_duplicates(subset=subset, keep=keep)

def clean_text(series, **kwargs):
    """
    Performs a variety of cleaning operations on a text Series.
    """
    if not isinstance(series.dtype, (object, str)):
        return series
    text = series.astype(str).copy()
    if kwargs.get('lowercase', True): text = text.str.lower()
    if kwargs.get('remove_punct', True): text = text.str.translate(str.maketrans('', '', string.punctuation))
    if kwargs.get('remove_digits', False): text = text.str.replace(r'\d+', '', regex=True)
    if kwargs.get('remove_stopwords', False):
        _ensure_nltk_data('stopwords')
        stop_words = set(nltk.corpus.stopwords.words(kwargs.get('lang', 'english')))
        text = text.apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
    if kwargs.get('remove_whitespace', True): text = text.str.strip().str.replace(r'\s+', ' ', regex=True)
    return text

def handle_rare_categories(df, column, threshold=0.01, label='Other'):
    """
    Groups rare categorical values into a single category.
    """
    df_copy = df.copy()
    if column not in df_copy.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    proportions = df_copy[column].value_counts(normalize=True)
    rare_categories = proportions[proportions < threshold].index
    df_copy[column] = df_copy[column].replace(rare_categories, label)
    return df_copy

