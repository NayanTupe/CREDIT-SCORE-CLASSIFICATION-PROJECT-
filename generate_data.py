"""
Generate sample credit score dataset for demonstration
"""
import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate sample data
n_samples = 2000

data = {
    'ID': range(1, n_samples + 1),
    'Customer_ID': [f'CUST_{i:05d}' for i in range(1, n_samples + 1)],
    'Age': np.random.randint(18, 70, n_samples),
    'Annual_Income': np.random.randint(20000, 200000, n_samples),
    'Monthly_Inhand_Salary': np.random.randint(1500, 15000, n_samples),
    'Monthly_Income': np.random.randint(2000, 20000, n_samples),
    'Monthly_Expenses': np.random.randint(1000, 10000, n_samples),
    'Outstanding_Debt': np.random.randint(0, 100000, n_samples),
    'Number_of_Loans': np.random.randint(0, 5, n_samples),
    'Credit_Utilization_Ratio': np.random.uniform(0, 1, n_samples),
    'Payment_Behaviour': np.random.choice(['Good', 'Poor'], n_samples),
    'Credit_Mix': np.random.choice(['Good', 'Standard', 'Poor'], n_samples),
    'Credit_History_Age': np.random.randint(1, 30, n_samples),
    'Num_Credit_Inquiries': np.random.randint(0, 10, n_samples),
    'Occupation': np.random.choice(['Software_Engineer', 'Teacher', 'Doctor', 'Accountant', 'Manager', 'Technician', 'Consultant'], n_samples),
    'Type_of_Loan': np.random.choice(['Personal_Loan', 'Home_Loan', 'Car_Loan', 'Credit_Card'], n_samples),
    'Payment_of_Min_Amount': np.random.choice(['Yes', 'No'], n_samples),
    'Num_Bank_Accounts': np.random.randint(1, 5, n_samples),
    'Num_Credit_Card': np.random.randint(0, 5, n_samples),
}

# Create target variable based on some features
credit_scores = []
for i in range(n_samples):
    score = 0
    # Income factor
    if data['Annual_Income'][i] > 100000:
        score += 30
    elif data['Annual_Income'][i] > 50000:
        score += 20
    else:
        score += 10
    
    # Payment behavior
    if data['Payment_Behaviour'][i] == 'Good':
        score += 30
    else:
        score -= 10
    
    # Debt factor
    debt_to_income = data['Outstanding_Debt'][i] / (data['Annual_Income'][i] + 1)
    if debt_to_income < 0.3:
        score += 20
    elif debt_to_income < 0.6:
        score += 10
    else:
        score -= 10
    
    # Add some randomness
    score += np.random.randint(-10, 10)
    
    # Assign class
    if score >= 50:
        credit_scores.append('Good')
    elif score >= 30:
        credit_scores.append('Standard')
    else:
        credit_scores.append('Poor')

data['Credit_Score'] = credit_scores

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('train.csv', index=False)
print("✓ Sample dataset created: train.csv")
print(f"  Shape: {df.shape}")
print(f"\nCredit Score Distribution:")
print(df['Credit_Score'].value_counts())
print(f"\nFirst 5 rows:")
print(df.head())
