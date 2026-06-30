# HostelWise AI - ETL Data Cleaning Pipeline
import pandas as pd
import numpy as np

# Permitted Categories
VALID_CATEGORIES = {
    'Food', 'Snacks', 'Travel', 'Shopping', 'Recharge', 
    'Entertainment', 'Medical', 'Education', 'Other'
}

def get_df_library(use_gpu=False):
    """Dynamically load cuDF or Pandas based on GPU preference and availability."""
    if use_gpu:
        try:
            import cudf  # type: ignore
            return cudf, True
        except ImportError:
            print("NVIDIA cuDF not available. Falling back to CPU Pandas.")
            return pd, False
    return pd, False

def clean_expense_data(file_path_or_df, use_gpu=False):
    """
    Clean and validate expense data.
    
    Operations:
    1. Handles missing values (fills subcategory/description).
    2. Removes duplicate transactions.
    3. Standardizes date formats.
    4. Normalizes and validates categories.
    5. Validates transaction amounts (ensures positive values).
    """
    db, is_gpu = get_df_library(use_gpu)
    
    # Load data
    if isinstance(file_path_or_df, str):
        df = db.read_csv(file_path_or_df)
    else:
        df = file_path_or_df
        if is_gpu and isinstance(df, pd.DataFrame):
            import cudf  # type: ignore
            df = cudf.DataFrame.from_pandas(df)
            
    if len(df) == 0:
        return df

    # 1. Missing Value Handling
    if 'subcategory' in df.columns:
        df['subcategory'] = df['subcategory'].fillna('General')
    else:
        df['subcategory'] = 'General'
        
    if 'description' in df.columns:
        df['description'] = df['description'].fillna('No description provided')
    else:
        df['description'] = 'No description provided'
        
    if 'payment_mode' in df.columns:
        df['payment_mode'] = df['payment_mode'].fillna('UPI')
    else:
        df['payment_mode'] = 'UPI'

    # 2. Duplicate Removal
    df = df.drop_duplicates()

    # 3. Date Standardization
    if is_gpu:
        df['date'] = db.to_datetime(df['date'], errors='coerce')
    else:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
    df = df.dropna(subset=['date'])

    # 4. Category Normalization
    if is_gpu:
        df['category'] = df['category'].str.strip().str.title()
        valid_mask = df['category'].isin(list(VALID_CATEGORIES))
        df.loc[~valid_mask, 'category'] = 'Other'
    else:
        df['category'] = df['category'].astype(str).str.strip().str.title()
        df['category'] = df['category'].apply(lambda x: x if x in VALID_CATEGORIES else 'Other')

    # 5. Amount Validation
    if is_gpu:
        df['amount'] = db.to_numeric(df['amount'], errors='coerce')
    else:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
    df = df.dropna(subset=['amount'])
    df = df[df['amount'] > 0]
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df
