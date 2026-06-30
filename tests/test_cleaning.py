# HostelWise AI - Unit Tests for Data Cleaning Pipeline
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import analytics modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analytics.clean import clean_expense_data

def test_clean_expense_data_valid():
    """Test cleaning on a completely valid dataset."""
    raw_data = {
        'date': ['2026-06-29 12:00:00', '2026-06-29 14:30:00'],
        'amount': [150.0, 450.50],
        'category': ['Food', 'Travel'],
        'subcategory': ['Mess', 'Cab'],
        'description': ['Lunch', 'Ride to hostel'],
        'payment_mode': ['UPI', 'Debit Card']
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_expense_data(df, use_gpu=False)
    
    assert len(cleaned_df) == 2
    assert cleaned_df['category'].iloc[0] == 'Food'
    assert cleaned_df['amount'].iloc[1] == 450.50

def test_clean_expense_data_duplicates_and_negatives():
    """Test that duplicates are removed and negative/zero amounts are filtered."""
    raw_data = {
        'date': ['2026-06-29 12:00:00', '2026-06-29 12:00:00', '2026-06-29 14:00:00', '2026-06-29 15:00:00'],
        'amount': [100.0, 100.0, -50.0, 0.0],
        'category': ['Food', 'Food', 'Snacks', 'Travel'],
        'subcategory': ['Canteen', 'Canteen', 'Tea', 'Auto'],
        'description': ['Tea', 'Tea', 'Tea', 'Ride'],
        'payment_mode': ['UPI', 'UPI', 'Cash', 'Cash']
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_expense_data(df, use_gpu=False)
    
    # Should only keep 1 unique row with positive amount (the first 100.0 row)
    assert len(cleaned_df) == 1
    assert cleaned_df['amount'].iloc[0] == 100.0

def test_clean_expense_data_category_normalization():
    """Test that invalid categories are normalized to 'Other'."""
    raw_data = {
        'date': ['2026-06-29 12:00:00', '2026-06-29 13:00:00'],
        'amount': [150.0, 500.0],
        'category': ['food', 'cryptocurrency_purchase'],  # 'food' should be capitalized, 'crypto' is invalid
        'subcategory': ['Mess', 'Investment'],
        'description': ['Dinner', 'Bitcoin'],
        'payment_mode': ['UPI', 'Debit Card']
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_expense_data(df, use_gpu=False)
    
    assert len(cleaned_df) == 2
    assert cleaned_df['category'].iloc[0] == 'Food'      # Capitalized
    assert cleaned_df['category'].iloc[1] == 'Other'     # Normalized to Other
