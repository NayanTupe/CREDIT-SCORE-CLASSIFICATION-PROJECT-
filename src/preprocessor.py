"""
Preprocessing and Feature Engineering Module
Handles encoding, scaling, and feature transformation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


class Preprocessor:
    """Handle preprocessing and feature engineering"""
    
    def __init__(self, df, target_column='Credit_Score'):
        """
        Initialize Preprocessor
        
        Args:
            df (DataFrame): Input data
            target_column (str): Target column name
        """
        self.df = df.copy()
        self.target_column = target_column
        self.label_encoders = {}
        self.preprocessor = None
        self.feature_names = None
        self.categorical_cols = []
        self.numeric_cols = []
    
    def identify_columns(self):
        """
        Identify categorical and numerical columns
        
        Returns:
            tuple: (categorical_cols, numeric_cols)
        """
        all_cols = self.df.columns.tolist()
        
        # Remove target column
        if self.target_column in all_cols:
            all_cols.remove(self.target_column)
        
        # Remove ID-like columns
        id_cols = [col for col in all_cols if col.lower() in ['id', 'customer_id', 'ssn', 'name']]
        for col in id_cols:
            if col in all_cols:
                all_cols.remove(col)
        
        self.categorical_cols = self.df[all_cols].select_dtypes(include=['object']).columns.tolist()
        self.numeric_cols = self.df[all_cols].select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        print(f"✓ Identified {len(self.numeric_cols)} numeric columns")
        print(f"✓ Identified {len(self.categorical_cols)} categorical columns")
        
        return self.categorical_cols, self.numeric_cols
    
    def engineer_features(self):
        """
        Create new features from existing ones
        
        Returns:
            DataFrame: Data with engineered features
        """
        print("\nEngineering new features...")
        
        # Example: Financial ratios (adapt based on your columns)
        if 'Annual_Income' in self.df.columns and 'Outstanding_Debt' in self.df.columns:
            self.df['Debt_to_Income_Ratio'] = (
                self.df['Outstanding_Debt'] / (self.df['Annual_Income'] + 1)
            )
            print("  ✓ Created: Debt_to_Income_Ratio")
        
        if 'Monthly_Inhand_Salary' in self.df.columns and 'Monthly_Income' in self.df.columns:
            self.df['Salary_to_Income_Ratio'] = (
                self.df['Monthly_Inhand_Salary'] / (self.df['Monthly_Income'] + 1)
            )
            print("  ✓ Created: Salary_to_Income_Ratio")
        
        # Payment consistency (if exists)
        if 'Payment_Behaviour' in self.df.columns:
            self.df['Good_Payment_Behavior'] = (
                self.df['Payment_Behaviour'].astype(str).str.contains('Good', case=False, na=False).astype(int)
            )
            print("  ✓ Created: Good_Payment_Behavior")
        
        return self.df
    
    def encode_categorical_features(self):
        """
        Encode categorical features using LabelEncoder
        
        Returns:
            DataFrame: Data with encoded categorical features
        """
        print("\nEncoding categorical features...")
        
        for col in self.categorical_cols:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col].astype(str))
            self.label_encoders[col] = le
            print(f"  ✓ Encoded: {col}")
        
        return self.df
    
    def encode_target(self):
        """
        Encode target variable
        
        Returns:
            tuple: (y_encoded, label_encoder, class_names)
        """
        print(f"\nEncoding target variable: {self.target_column}")
        
        le = LabelEncoder()
        y = le.fit_transform(self.df[self.target_column].astype(str))
        
        print(f"  ✓ Target classes: {list(le.classes_)}")
        print(f"  ✓ Class distribution:")
        unique, counts = np.unique(y, return_counts=True)
        for cls, count in zip(le.classes_, counts):
            pct = (count / len(y)) * 100
            print(f"    - {cls}: {count} ({pct:.1f}%)")
        
        return y, le, le.classes_
    
    def create_preprocessing_pipeline(self):
        """
        Create sklearn preprocessing pipeline
        
        Returns:
            ColumnTransformer: Preprocessing pipeline
        """
        print("\nCreating preprocessing pipeline...")
        
        self.preprocessor = ColumnTransformer([
            ('numeric', StandardScaler(), self.numeric_cols),
            ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             self.categorical_cols)
        ], remainder='drop')
        
        print(f"  ✓ Scaling {len(self.numeric_cols)} numeric features")
        print(f"  ✓ One-hot encoding {len(self.categorical_cols)} categorical features")
        
        return self.preprocessor
    
    def fit_preprocessor(self, X):
        """
        Fit preprocessor on training data
        
        Args:
            X (DataFrame): Training features
        
        Returns:
            ndarray: Transformed training data
        """
        if self.preprocessor is None:
            self.create_preprocessing_pipeline()
        
        X_transformed = self.preprocessor.fit_transform(X)
        
        # Get feature names after transformation
        feature_names = []
        feature_names.extend(self.numeric_cols)
        
        # Add one-hot encoded feature names
        if len(self.categorical_cols) > 0:
            ohe = self.preprocessor.named_transformers_['categorical']
            cat_features = ohe.get_feature_names_out(self.categorical_cols)
            feature_names.extend(cat_features)
        
        self.feature_names = feature_names
        
        print(f"\n✓ Preprocessor fitted")
        print(f"  Output shape: {X_transformed.shape}")
        print(f"  Total features after preprocessing: {len(self.feature_names)}")
        
        return X_transformed
    
    def transform(self, X):
        """
        Transform new data using fitted preprocessor
        
        Args:
            X (DataFrame): Features to transform
        
        Returns:
            ndarray: Transformed data
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor not fitted yet. Call fit_preprocessor() first.")
        
        return self.preprocessor.transform(X)
    
    def get_feature_names(self):
        """Get feature names after preprocessing"""
        return self.feature_names
    
    def get_processed_data(self):
        """Return processed dataframe"""
        return self.df


# Example usage
if __name__ == "__main__":
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader('train.csv')
    df = loader.load_data()
    df = loader.handle_missing_values()
    df = loader.remove_duplicates()
    
    # Preprocess
    preprocessor = Preprocessor(df)
    preprocessor.identify_columns()
    preprocessor.engineer_features()
    preprocessor.encode_categorical_features()
    
    y, le, classes = preprocessor.encode_target()
    
    # Prepare features and target
    X = df.drop('Credit_Score', axis=1)
    
    # Fit preprocessor
    X_transformed = preprocessor.fit_preprocessor(X)
    
    print(f"\nFinal shapes:")
    print(f"  X: {X_transformed.shape}")
    print(f"  y: {y.shape}")
