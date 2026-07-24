"""
Machine Learning Models Module
Defines and configures different classification models
"""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
# XGBoost removed due to OpenMP dependency issues on Mac systems
# Using GradientBoostingClassifier as replacement
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import pandas as pd


class ModelFactory:
    """Create different ML models with default parameters"""
    
    @staticmethod
    def get_logistic_regression():
        """
        Create Logistic Regression model
        
        Returns:
            LogisticRegression: Model instance
        """
        return LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
    
    @staticmethod
    def get_random_forest(n_estimators=100):
        """
        Create Random Forest Classifier
        
        Args:
            n_estimators (int): Number of trees
        
        Returns:
            RandomForestClassifier: Model instance
        """
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
    
    @staticmethod
    def get_gradient_boosting(n_estimators=100):
        """
        Create Gradient Boosting Classifier (sklearn alternative to XGBoost)
        
        Args:
            n_estimators (int): Number of boosting rounds
        
        Returns:
            GradientBoostingClassifier: Model instance
        """
        return GradientBoostingClassifier(
            n_estimators=n_estimators,
            learning_rate=0.1,
            max_depth=6,
            subsample=0.8,
            random_state=42
        )


class ModelTrainer:
    """Train and evaluate models"""
    
    def __init__(self, model, X_train, X_test, y_train, y_test):
        """
        Initialize ModelTrainer
        
        Args:
            model: Model instance
            X_train, X_test: Training and testing features
            y_train, y_test: Training and testing labels
        """
        self.model = model
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.best_model = None
        self.best_params = None
    
    def train(self):
        """
        Train model on training data
        
        Returns:
            Trained model
        """
        print(f"\nTraining {self.model.__class__.__name__}...")
        self.model.fit(self.X_train, self.y_train)
        print(f"✓ {self.model.__class__.__name__} training completed")
        
        return self.model
    
    def cross_validate(self, cv=5):
        """
        Perform cross-validation
        
        Args:
            cv (int): Number of folds
        
        Returns:
            dict: Cross-validation scores
        """
        from sklearn.model_selection import cross_validate
        
        print(f"\nPerforming {cv}-fold cross-validation...")
        
        scoring = {
            'accuracy': 'accuracy',
            'precision_weighted': 'precision_weighted',
            'recall_weighted': 'recall_weighted',
            'f1_weighted': 'f1_weighted'
        }
        
        cv_results = cross_validate(
            self.model, self.X_train, self.y_train,
            cv=cv, scoring=scoring, return_train_score=True
        )
        
        # Print results
        print(f"\nCross-Validation Results ({cv}-fold):")
        for metric in ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']:
            test_scores = cv_results[f'test_{metric}']
            print(f"  {metric:20s}: {test_scores.mean():.4f} (± {test_scores.std():.4f})")
        
        return cv_results
    
    def hyperparameter_tuning(self, param_grid, cv=5):
        """
        Perform hyperparameter tuning using GridSearchCV
        
        Args:
            param_grid (dict): Parameter grid for search
            cv (int): Number of folds
        
        Returns:
            Best model and best parameters
        """
        print(f"\nPerforming hyperparameter tuning for {self.model.__class__.__name__}...")
        print(f"  Parameters to tune: {list(param_grid.keys())}")
        
        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=cv,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        self.best_model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        print(f"\n✓ Best Parameters Found:")
        for param, value in self.best_params.items():
            print(f"  {param}: {value}")
        print(f"\n  Best CV Score: {grid_search.best_score_:.4f}")
        
        return self.best_model, self.best_params
    
    def get_feature_importance(self, feature_names=None):
        """
        Get feature importance (for tree-based models)
        
        Args:
            feature_names (list): Feature names
        
        Returns:
            DataFrame: Feature importance scores
        """
        if not hasattr(self.best_model or self.model, 'feature_importances_'):
            return None
        
        model = self.best_model if self.best_model else self.model
        importances = model.feature_importances_
        
        if feature_names is None:
            feature_names = [f'Feature_{i}' for i in range(len(importances))]
        
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        return importance_df


class EnsembleModel:
    """Create ensemble models"""
    
    @staticmethod
    def create_voting_classifier(X_train, y_train, X_test, y_test):
        """
        Create Voting Classifier combining multiple models
        
        Returns:
            VotingClassifier: Ensemble model
        """
        print("\nCreating Voting Classifier Ensemble...")
        
        lr = ModelFactory.get_logistic_regression()
        rf = ModelFactory.get_random_forest(n_estimators=100)
        gb = ModelFactory.get_gradient_boosting(n_estimators=100)
        
        voting_clf = VotingClassifier(
            estimators=[('lr', lr), ('rf', rf), ('gb', gb)],
            voting='soft'
        )
        
        print("✓ Voting Classifier created with: Logistic Regression, Random Forest, Gradient Boosting")
        
        return voting_clf


# Example usage
if __name__ == "__main__":
    from sklearn.model_selection import train_test_split
    from data_loader import DataLoader
    from preprocessor import Preprocessor
    
    # Load and preprocess data
    loader = DataLoader('train.csv')
    df = loader.load_data()
    df = loader.handle_missing_values()
    
    preprocessor = Preprocessor(df)
    preprocessor.identify_columns()
    preprocessor.engineer_features()
    preprocessor.encode_categorical_features()
    
    y, le, classes = preprocessor.encode_target()
    X = df.drop('Credit_Score', axis=1)
    
    X_transformed = preprocessor.fit_preprocessor(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_transformed, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train models
    print("="*60)
    print("TRAINING MODELS")
    print("="*60)
    
    for model_name, model_func in [
        ('Logistic Regression', ModelFactory.get_logistic_regression),
        ('Random Forest', ModelFactory.get_random_forest),
        ('XGBoost', ModelFactory.get_xgboost)
    ]:
        model = model_func()
        trainer = ModelTrainer(model, X_train, X_test, y_train, y_test)
        trainer.train()
        trainer.cross_validate(cv=5)
