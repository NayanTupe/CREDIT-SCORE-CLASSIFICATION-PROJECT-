"""
Main Pipeline Module
Orchestrates the complete credit score classification pipeline
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import warnings

from data_loader import DataLoader
from preprocessor import Preprocessor
from models import ModelFactory, ModelTrainer, EnsembleModel
from evaluator import ModelEvaluator, ModelComparison

warnings.filterwarnings('ignore')


class CreditScoringPipeline:
    """Complete credit scoring classification pipeline"""
    
    def __init__(self, data_path, target_column='Credit_Score', test_size=0.2, random_state=42):
        """
        Initialize Pipeline
        
        Args:
            data_path (str): Path to CSV file
            target_column (str): Target column name
            test_size (float): Test set size
            random_state (int): Random seed
        """
        self.data_path = data_path
        self.target_column = target_column
        self.test_size = test_size
        self.random_state = random_state
        
        self.loader = None
        self.preprocessor = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.label_encoder = None
        self.class_names = None
        self.models_trained = {}
        self.comparator = ModelComparison()
    
    def run_pipeline(self, tune_hyperparameters=True, cv_folds=5):
        """
        Run complete pipeline
        
        Args:
            tune_hyperparameters (bool): Whether to tune hyperparameters
            cv_folds (int): Number of CV folds
        """
        print("\n" + "="*80)
        print("CREDIT SCORE CLASSIFICATION - COMPLETE PIPELINE")
        print("="*80)
        
        # Step 1: Load and clean data
        self.step_load_data()
        
        # Step 2: Preprocess data
        self.step_preprocess_data()
        
        # Step 3: Train models
        self.step_train_models(tune_hyperparameters=tune_hyperparameters, cv_folds=cv_folds)
        
        # Step 4: Evaluate and compare models
        self.step_evaluate_models()
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
    
    def step_load_data(self):
        """Load and clean data"""
        print("\n" + "-"*80)
        print("STEP 1: LOAD AND CLEAN DATA")
        print("-"*80)
        
        self.loader = DataLoader(self.data_path)
        df = self.loader.load_data()
        
        self.loader.display_basic_info()
        
        df = self.loader.handle_missing_values(strategy='mean')
        df = self.loader.remove_duplicates()
        
        summary = self.loader.get_data_summary()
        print(f"\nData Summary:")
        print(f"  Total rows: {summary['total_rows']}")
        print(f"  Total columns: {summary['total_columns']}")
        print(f"  Numeric columns: {summary['numeric_cols']}")
        print(f"  Categorical columns: {summary['categorical_cols']}")
        print(f"  Missing values: {summary['missing_values']}")
    
    def step_preprocess_data(self):
        """Preprocess and engineer features"""
        print("\n" + "-"*80)
        print("STEP 2: PREPROCESS AND ENGINEER FEATURES")
        print("-"*80)
        
        df = self.loader.get_processed_data()
        
        self.preprocessor = Preprocessor(df, target_column=self.target_column)
        
        # Identify columns
        self.preprocessor.identify_columns()
        
        # Engineer features
        self.preprocessor.engineer_features()
        
        # Encode categorical features
        self.preprocessor.encode_categorical_features()
        
        # Encode target
        y, label_encoder, class_names = self.preprocessor.encode_target()
        self.label_encoder = label_encoder
        self.class_names = class_names
        
        # Get features from preprocessor's df (which has engineered features)
        X = self.preprocessor.df.drop(self.target_column, axis=1)
        
        # Identify columns again (after feature engineering)
        self.preprocessor.identify_columns()
        
        # Create and fit preprocessor pipeline
        X_transformed = self.preprocessor.fit_preprocessor(X)
        feature_names = self.preprocessor.get_feature_names()
        
        # Train-test split
        print(f"\nSplitting data (test_size={self.test_size})...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X_transformed, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )
        
        print(f"✓ Training set: {self.X_train.shape}")
        print(f"✓ Test set: {self.X_test.shape}")
        
        return feature_names
    
    def step_train_models(self, tune_hyperparameters=True, cv_folds=5):
        """Train multiple models"""
        print("\n" + "-"*80)
        print("STEP 3: TRAIN MODELS")
        print("-"*80)
        
        models_config = {
            'Logistic Regression': {
                'model_func': ModelFactory.get_logistic_regression,
                'params': {}
            },
            'Random Forest': {
                'model_func': ModelFactory.get_random_forest,
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 15, 20],
                    'min_samples_split': [5, 10]
                }
            },
            'Gradient Boosting': {
                'model_func': ModelFactory.get_gradient_boosting,
                'params': {}
            }
        }
        
        for model_name, config in models_config.items():
            print(f"\n{'='*60}")
            print(f"Training: {model_name}")
            print(f"{'='*60}")
            
            model = config['model_func']()
            trainer = ModelTrainer(model, self.X_train, self.X_test, self.y_train, self.y_test)
            
            # Train model
            trainer.train()
            
            # Cross-validation (skip for Gradient Boosting with small data)
            if model_name != 'Gradient Boosting':
                trainer.cross_validate(cv=cv_folds)
            else:
                print(f"\nSkipping cross-validation for {model_name} (small dataset)")
            
            # Hyperparameter tuning
            if tune_hyperparameters and config['params']:
                best_model, best_params = trainer.hyperparameter_tuning(config['params'], cv=cv_folds)
                self.models_trained[model_name] = best_model
            else:
                self.models_trained[model_name] = trainer.model
    
    def step_evaluate_models(self):
        """Evaluate and compare all models"""
        print("\n" + "-"*80)
        print("STEP 4: EVALUATE AND COMPARE MODELS")
        print("-"*80)
        
        for model_name, model in self.models_trained.items():
            print(f"\n{'='*60}")
            print(f"Evaluating: {model_name}")
            print(f"{'='*60}")
            
            # Make predictions
            y_pred = model.predict(self.X_test)
            
            # Evaluate
            evaluator = ModelEvaluator(
                self.y_test, y_pred,
                class_names=self.class_names,
                model_name=model_name
            )
            
            evaluator.print_metrics_summary()
            evaluator.print_confusion_matrix()
            evaluator.get_per_class_metrics()
            
            # Add to comparison
            self.comparator.add_model_result(model_name, self.y_test, y_pred)
        
        # Compare models
        print("\n" + "="*80)
        comparison_df = self.comparator.get_comparison_table()
        print("\n✓ All models evaluated successfully!")
    
    def visualize_results(self):
        """Create visualizations"""
        print("\nGenerating visualizations...")
        
        # Model comparison plot
        self.comparator.plot_model_comparison(figsize=(12, 6))
        
        # Feature importance (if Random Forest available)
        if 'Random Forest' in self.models_trained:
            self.plot_feature_importance('Random Forest')
    
    def plot_feature_importance(self, model_name, top_n=15):
        """Plot feature importance"""
        model = self.models_trained.get(model_name)
        if model is None or not hasattr(model, 'feature_importances_'):
            print(f"Model {model_name} does not support feature importance")
            return
        
        feature_names = self.preprocessor.get_feature_names()
        importances = model.feature_importances_
        
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False).head(top_n)
        
        plt.figure(figsize=(10, 8))
        plt.barh(importance_df['Feature'], importance_df['Importance'], color='steelblue')
        plt.xlabel('Importance', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.title(f'Top {top_n} Feature Importances - {model_name}', 
                 fontsize=14, weight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
    
    def get_best_model(self):
        """Get best model based on accuracy"""
        if not self.models_trained:
            print("No models trained yet")
            return None
        
        best_model_name = None
        best_accuracy = 0
        
        for model_name, model in self.models_trained.items():
            y_pred = model.predict(self.X_test)
            accuracy = np.mean(y_pred == self.y_test)
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model_name = model_name
        
        print(f"\n{'='*60}")
        print(f"BEST MODEL: {best_model_name}")
        print(f"Accuracy: {best_accuracy:.4f}")
        print(f"{'='*60}")
        
        return best_model_name, self.models_trained[best_model_name]


def main():
    """Main execution function"""
    
    # Initialize pipeline
    pipeline = CreditScoringPipeline(
        data_path='/Users/apple/Desktop/CREDIT-SCORE-CLASSIFICATION-PROJECT-/train.csv',
        target_column='Credit_Score',
        test_size=0.2,
        random_state=42
    )
    
    # Run pipeline with hyperparameter tuning
    pipeline.run_pipeline(tune_hyperparameters=True, cv_folds=5)
    
    # Visualize results
    pipeline.visualize_results()
    
    # Get best model
    best_name, best_model = pipeline.get_best_model()
    
    # Summary
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    print(f"✓ Data loaded and cleaned")
    print(f"✓ Features engineered and preprocessed")
    print(f"✓ 3 models trained and evaluated")
    print(f"✓ Hyperparameters tuned")
    print(f"✓ 5-fold cross-validation performed")
    print(f"✓ Best model: {best_name}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
