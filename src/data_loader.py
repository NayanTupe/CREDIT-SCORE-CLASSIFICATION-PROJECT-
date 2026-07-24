"""
Data Loading and Cleaning Module
Handles loading CSV data, checking data quality, and cleaning
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer           // Added for missing value imputation sklearn.impute use for handling missing values

class DataLoader:
    """Load and clean credit score classification data"""
    
    def __init__(self, filepath):        // Initialize DataLoader with file path running the code will load the data from the specified CSV file and perform basic data quality checks and cleaning operations. The class provides methods to handle missing values, remove duplicates, and identify outliers in the dataset.
        """
        Initialize DataLoader
        
        Args:
            filepath (str): Path to CSV file
        """
        self.filepath = filepath   // Store the file path for later use when loading the data
        self.df = None                  // DataFrame to hold the loaded data intially set to None until the data is loaded
        self.original_shape = None        // Store the original shape of the dataset for reference after loading the data, this can be useful for tracking changes in the dataset after cleaning operations are performed.
    
    def load_data(self):             // function to load csv data from the specified file path and store it in a DataFrame. It also prints out the shape of the loaded dataset for verification.
        """
        Load CSV data
        
        Returns:    
            DataFrame: Loaded data
        """
        print(f"Loading data from {self.filepath}...")     // Print a message indicating the file being loaded.     f = formatted string.
        self.df = pd.read_csv(self.filepath, low_memory=False)
        self.original_shape = self.df.shape
        print(f"✓ Data loaded successfully!")
        print(f"  Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        return self.df
    
    def display_basic_info(self):
        """Display basic information about dataset"""
        print("\n" + "="*60)
        print("DATASET INFORMATION")
        print("="*60)
        
        print(f"\nDataset Shape: {self.df.shape}")
        
        print("\nData Types:")
        print(self.df.dtypes)
        
        print("\nMissing Values:")
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing_Count': missing.values,
            'Percentage': missing_pct.values
        })
        print(missing_df[missing_df['Missing_Count'] > 0])
        
        print("\nBasic Statistics:")
        print(self.df.describe())
    
    def handle_missing_values(self, strategy='mean'):
        """
        Handle missing values in dataset
        
        Args:
            strategy (str): Imputation strategy ('mean', 'median', 'mode')
        
        Returns:
            DataFrame: Data with missing values handled
        """
        print(f"\nHandling missing values with strategy: '{strategy}'")
        
        # Get numeric and categorical columns
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        # Impute numeric columns
        if len(numeric_cols) > 0:
            imputer = SimpleImputer(strategy=strategy)
            self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
            print(f"✓ Imputed {len(numeric_cols)} numeric columns")
        
        # Drop rows with missing categorical values (or fill with mode)
        if len(categorical_cols) > 0:
            self.df[categorical_cols] = self.df[categorical_cols].fillna(
                self.df[categorical_cols].mode().iloc[0]
            )
            print(f"✓ Filled {len(categorical_cols)} categorical columns")
        
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            print(f"\nRemoving {duplicates} duplicate rows...")
            self.df.drop_duplicates(inplace=True)
            print(f"✓ Removed duplicates")
        else:
            print("\n✓ No duplicates found")
        
        return self.df
    
    def remove_outliers(self, columns=None, method='iqr', threshold=1.5):
        """
        Remove outliers from numeric columns
        
        Args:
            columns (list): Columns to check for outliers. If None, use all numeric
            method (str): 'iqr' for Interquartile Range
            threshold (float): IQR multiplier (default 1.5)
        
        Returns:
            DataFrame: Data without outliers
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['int64', 'float64']).columns
        
        print(f"\nRemoving outliers using {method} method...")
        initial_rows = len(self.df)
        
        if method == 'iqr':
            for col in columns:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
        
        removed = initial_rows - len(self.df)
        print(f"✓ Removed {removed} outlier rows")
        
        return self.df
    
    def get_data_summary(self):
        """Get summary statistics"""
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'numeric_cols': len(self.df.select_dtypes(include=['int64', 'float64']).columns),
            'categorical_cols': len(self.df.select_dtypes(include=['object']).columns),
            'missing_values': self.df.isnull().sum().sum()
        }
    
    def get_processed_data(self):
        """Return processed dataframe"""
        return self.df


# Example usage
if __name__ == "__main__":
    loader = DataLoader('train.csv')
    df = loader.load_data()
    loader.display_basic_info()
    df = loader.handle_missing_values(strategy='mean')
    df = loader.remove_duplicates()
    # df = loader.remove_outliers()  # Uncomment if needed
    print(f"\nFinal shape: {df.shape}")
