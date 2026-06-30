# HostelWise AI - Mock Student Expense Data Generator
import csv
import random
import argparse
from datetime import datetime, timedelta
import os

# Categories and Subcategories
EXPENSE_CATEGORIES = {
    'Food': ['Hostel Mess', 'Restaurant', 'Zomato/Swiggy', 'Groceries'],
    'Snacks': ['Tea/Coffee', 'Maggi & Noodles', 'Chips & Biscuits', 'Juice & Shakes'],
    'Travel': ['Auto/E-Rickshaw', 'Uber/Ola Cab', 'Metro Fare', 'Train/Flight Home'],
    'Shopping': ['Clothes', 'Footwear', 'Electronics', 'Toiletries'],
    'Recharge': ['Mobile Data', 'Hostel Wi-Fi', 'OTT Subscription'],
    'Entertainment': ['Netflix/Spotify', 'Movie Ticket', 'Gaming Parlor', 'Weekend Outing'],
    'Medical': ['Pharmacy', 'Doctor Consultation', 'First Aid'],
    'Education': ['Reference Books', 'Stationery', 'Exam Registration', 'Online Course'],
    'Other': ['Laundry Services', 'Hostel Security', 'Miscellaneous']
}

PAYMENT_MODES = ['UPI', 'Cash', 'Debit Card', 'Credit Card']

# Probability weights for categories (students spend most on Food, Snacks, Travel)
CATEGORY_WEIGHTS = {
    'Food': 0.30,
    'Snacks': 0.20,
    'Travel': 0.15,
    'Shopping': 0.10,
    'Recharge': 0.08,
    'Entertainment': 0.07,
    'Medical': 0.03,
    'Education': 0.05,
    'Other': 0.02
}

def get_random_amount(category, subcategory):
    """Generate realistic amounts in Indian Rupees (₹) based on category."""
    if category == 'Food':
        if subcategory == 'Hostel Mess':
            return round(random.uniform(2000, 3500), 2)  # Monthly mess fee
        elif subcategory == 'Restaurant':
            return round(random.uniform(250, 800), 2)
        elif subcategory == 'Zomato/Swiggy':
            return round(random.uniform(150, 450), 2)
        else:
            return round(random.uniform(50, 250), 2)
            
    elif category == 'Snacks':
        if subcategory == 'Tea/Coffee':
            return round(random.uniform(10, 40), 2)
        elif subcategory == 'Maggi & Noodles':
            return round(random.uniform(20, 80), 2)
        else:
            return round(random.uniform(15, 120), 2)
            
    elif category == 'Travel':
        if subcategory == 'Train/Flight Home':
            return round(random.uniform(1200, 6500), 2)
        elif subcategory == 'Uber/Ola Cab':
            return round(random.uniform(150, 600), 2)
        else:
            return round(random.uniform(10, 60), 2)
            
    elif category == 'Shopping':
        if subcategory == 'Electronics':
            return round(random.uniform(999, 15000), 2)
        elif subcategory == 'Clothes' or subcategory == 'Footwear':
            return round(random.uniform(500, 3000), 2)
        else:
            return round(random.uniform(50, 400), 2)
            
    elif category == 'Recharge':
        if subcategory == 'Mobile Data':
            return round(random.choice([199, 299, 666, 719, 839]), 2)
        elif subcategory == 'Hostel Wi-Fi':
            return round(random.uniform(400, 800), 2)
        else:
            return round(random.choice([149, 299, 499]), 2)
            
    elif category == 'Entertainment':
        if subcategory == 'Weekend Outing':
            return round(random.uniform(500, 2500), 2)
        elif subcategory == 'Netflix/Spotify':
            return round(random.choice([149, 199, 299, 649]), 2)
        else:
            return round(random.uniform(120, 500), 2)
            
    elif category == 'Medical':
        if subcategory == 'Doctor Consultation':
            return round(random.choice([200, 300, 500]), 2)
        else:
            return round(random.uniform(20, 1500), 2)
            
    elif category == 'Education':
        if subcategory == 'Online Course':
            return round(random.uniform(499, 4999), 2)
        elif subcategory == 'Exam Registration':
            return round(random.uniform(1000, 2500), 2)
        else:
            return round(random.uniform(20, 500), 2)
            
    else:  # Other
        return round(random.uniform(50, 1000), 2)

def generate_dataset(num_rows, output_file):
    """Generate a CSV file with synthetic student expense data."""
    start_date = datetime.now() - timedelta(days=365)
    
    print(f"Generating {num_rows} expense records...")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Header
        writer.writerow(['date', 'amount', 'category', 'subcategory', 'description', 'payment_mode'])
        
        categories = list(CATEGORY_WEIGHTS.keys())
        weights = list(CATEGORY_WEIGHTS.values())
        
        for i in range(num_rows):
            # 1. Date Generation
            # Spread dates over the last 365 days. 
            # We add a slight bias to have more transactions in recent months.
            bias_days = int(random.triangular(0, 365, 365))
            tx_date = start_date + timedelta(days=bias_days)
            # Add random hour/minute
            tx_datetime = tx_date.replace(
                hour=random.randint(8, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            date_str = tx_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            # 2. Category & Subcategory Selection
            category = random.choices(categories, weights=weights, k=1)[0]
            subcategory = random.choice(EXPENSE_CATEGORIES[category])
            
            # 3. Temporal adjustments (e.g. Mess fees/recharges happen in 1st week)
            is_first_week = tx_datetime.day <= 7
            is_weekend = tx_datetime.weekday() >= 5 # 5=Sat, 6=Sun
            
            if category == 'Food' and subcategory == 'Hostel Mess' and not is_first_week:
                # Mess fees only in first week, swap to restaurant/zomato
                subcategory = random.choice(['Restaurant', 'Zomato/Swiggy', 'Groceries'])
            
            if is_first_week and random.random() < 0.3:
                # First week bias: higher chance of Recharges, Rent (Other), Books (Education)
                category = random.choice(['Recharge', 'Education', 'Food'])
                subcategory = random.choice(EXPENSE_CATEGORIES[category])
                
            if is_weekend and random.random() < 0.4:
                # Weekend bias: higher chance of Entertainment, Shopping, Restaurants
                category = random.choice(['Entertainment', 'Shopping', 'Food'])
                if category == 'Food':
                    subcategory = random.choice(['Restaurant', 'Zomato/Swiggy'])
                else:
                    subcategory = random.choice(EXPENSE_CATEGORIES[category])

            # 4. Amount Generation
            amount = get_random_amount(category, subcategory)
            
            # 5. Description
            description = f"Paid for {subcategory.lower()}"
            if category == 'Food' and subcategory == 'Zomato/Swiggy':
                description = random.choice(['Biryani order', 'Burger & Fries', 'Pizza party', 'Late night dessert'])
            elif category == 'Snacks' and subcategory == 'Tea/Coffee':
                description = random.choice(['Chai at tapri', 'Cold coffee at canteen', 'Chai & biscuits'])
            elif category == 'Travel' and subcategory == 'Auto/E-Rickshaw':
                description = random.choice(['Auto to college', 'Rickshaw from metro station', 'Shared auto to market'])
            elif category == 'Entertainment' and subcategory == 'Movie Ticket':
                description = random.choice(['Movie with hostel mates', 'Popcorn and ticket', 'IMAX show'])

            # 6. Payment Mode
            # UPI is highly popular for small amounts. Cards for large amounts.
            if amount < 150:
                payment_mode = random.choices(['UPI', 'Cash'], weights=[0.85, 0.15], k=1)[0]
            elif amount > 2000:
                payment_mode = random.choices(['Debit Card', 'Credit Card', 'UPI'], weights=[0.5, 0.3, 0.2], k=1)[0]
            else:
                payment_mode = random.choices(['UPI', 'Debit Card', 'Cash', 'Credit Card'], weights=[0.6, 0.2, 0.1, 0.1], k=1)[0]
                
            writer.writerow([date_str, amount, category, subcategory, description, payment_mode])
            
            # Progress update
            if (i + 1) % 250000 == 0:
                print(f"Generated {i + 1} rows...")
                
    print(f"Dataset saved successfully to {output_file}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate synthetic student expense datasets.")
    parser.add_argument('--rows', type=int, default=5000, help="Number of rows to generate (default: 5000)")
    parser.add_argument('--output', type=str, default=None, help="Output file path")
    parser.add_argument('--benchmark', action='store_true', help="Generate all benchmark files (100K, 500K, 1M)")
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.benchmark:
        # Generate files for benchmarking
        generate_dataset(100000, os.path.join(base_dir, 'benchmark_100k.csv'))
        generate_dataset(500000, os.path.join(base_dir, 'benchmark_500k.csv'))
        generate_dataset(1000000, os.path.join(base_dir, 'benchmark_1m.csv'))
    else:
        output = args.output if args.output else os.path.join(base_dir, 'student_expenses_sample.csv')
        generate_dataset(args.rows, output)
