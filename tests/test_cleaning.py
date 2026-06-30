# HostelWise AI - Unit Tests for Data Cleaning Pipeline
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import analytics modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analytics.clean import clean_expense_data

class TestCleaningPipeline(unittest.TestCase):
    def test_clean_expense_data_valid(self):
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
        
        self.assertEqual(len(cleaned_df), 2)
        self.assertEqual(cleaned_df['category'].iloc[0], 'Food')
        self.assertEqual(cleaned_df['amount'].iloc[1], 450.50)

    def test_clean_expense_data_duplicates_and_negatives(self):
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
        
        # Should only keep 1 unique row with positive amount
        self.assertEqual(len(cleaned_df), 1)
        self.assertEqual(cleaned_df['amount'].iloc[0], 100.0)

    def test_clean_expense_data_category_normalization(self):
        """Test that invalid categories are normalized to 'Other'."""
        raw_data = {
            'date': ['2026-06-29 12:00:00', '2026-06-29 13:00:00'],
            'amount': [150.0, 500.0],
            'category': ['food', 'cryptocurrency_purchase'],
            'subcategory': ['Mess', 'Investment'],
            'description': ['Dinner', 'Bitcoin'],
            'payment_mode': ['UPI', 'Debit Card']
        }
        df = pd.DataFrame(raw_data)
        cleaned_df = clean_expense_data(df, use_gpu=False)
        
        self.assertEqual(len(cleaned_df), 2)
        self.assertEqual(cleaned_df['category'].iloc[0], 'Food')
        self.assertEqual(cleaned_df['category'].iloc[1], 'Other')

if __name__ == '__main__':
    unittest.main()
