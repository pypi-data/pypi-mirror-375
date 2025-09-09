"""
Data quality and exploratory data analysis visualization functions.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import get_numeric_columns, get_categorical_columns

def plot_missing_values(df):
    """
    Generates a heatmap to visualize the distribution of missing values.

    Args:
        df (pd.DataFrame): The input DataFrame.
    """
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title('Missing Value Heatmap')
    plt.show()

def generate_report(df):
    """
    Generates a comprehensive data quality report as a dictionary.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary containing the data quality report.
    """
    report = {
        'overview': {
            'num_rows': len(df),
            'num_cols': len(df.columns),
            'total_missing': int(df.isnull().sum().sum()),
            'percent_missing': f"{df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100:.2f}%",
            'num_duplicates': int(df.duplicated().sum())
        },
        'columns': {}
    }

    for col in df.columns:
        col_report = {
            'dtype': str(df[col].dtype),
            'missing': int(df[col].isnull().sum()),
            'missing_percent': f"{df[col].isnull().sum() / len(df) * 100:.2f}%",
            'unique_values': int(df[col].nunique())
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_report['mean'] = float(df[col].mean())
            col_report['std'] = float(df[col].std())
            col_report['min'] = float(df[col].min())
            col_report['max'] = float(df[col].max())
        else:
            col_report['top_5_frequent'] = df[col].value_counts().nlargest(5).to_dict()

        report['columns'][col] = col_report
        
    return report

# --- NEW FEATURES ---

def plot_distribution(df, column):
    """
    Plots the distribution of a single column.
    Histogram for numeric, bar chart for categorical.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): The column name to plot.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    plt.figure(figsize=(10, 6))
    if pd.api.types.is_numeric_dtype(df[column]):
        sns.histplot(df[column], kde=True)
        plt.title(f'Distribution of {column} (Numeric)')
    else:
        # For categorical, show top 15 most frequent values
        top_n = 15
        counts = df[column].value_counts()
        if len(counts) > top_n:
            counts = counts.nlargest(top_n)
            plt.title(f'Top {top_n} Frequencies for {column} (Categorical)')
        else:
            plt.title(f'Frequencies for {column} (Categorical)')
        sns.barplot(x=counts.index, y=counts.values)
        plt.xticks(rotation=45)
    
    plt.xlabel(column)
    plt.ylabel('Frequency' if pd.api.types.is_numeric_dtype(df[column]) else 'Count')
    plt.tight_layout()
    plt.show()

def plot_correlation_heatmap(df):
    """
    Plots a correlation heatmap for the numeric columns in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
    """
    numeric_cols = get_numeric_columns(df)
    if len(numeric_cols) < 2:
        print("Not enough numeric columns to plot a correlation heatmap.")
        return

    plt.figure(figsize=(12, 10))
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap of Numeric Features')
    plt.show()

def plot_outliers(df, column):
    """
    Creates a box plot to visually identify outliers in a numeric column.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): The numeric column to plot.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    if not pd.api.types.is_numeric_dtype(df[column]):
        print(f"Column '{column}' is not numeric. Box plot is not applicable.")
        return

    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[column])
    plt.title(f'Box Plot for Outlier Detection in {column}')
    plt.xlabel(column)
    plt.show()

