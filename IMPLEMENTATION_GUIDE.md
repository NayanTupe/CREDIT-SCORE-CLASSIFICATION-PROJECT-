# 🛠️ IMPROVEMENT IMPLEMENTATION GUIDE

## Quick Reference for Each Improvement

---

## 1️⃣ PROPER PROJECT STRUCTURE

### Create Directory Structure
```bash
mkdir -p src models reports tests data
```

### Create `src/data_loader.py`
```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
    
    def load_data(self):
        """Load CSV data"""
        self.df = pd.read_csv(self.filepath, low_memory=False)
        return self.df
    
    def basic_info(self):
        """Print data information"""
        print(f"Shape: {self.df.shape}")
        print(f"\nMissing Values:\n{self.df.isnull().sum()}")
        print(f"\nData Types:\n{self.df.dtypes}")
    
    def handle_missing_values(self, strategy='mean'):
        """Handle missing values"""
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        imputer = SimpleImputer(strategy=strategy)
        self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
        
        # Drop remaining rows with missing values
        self.df.dropna(inplace=True)
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        self.df.drop_duplicates(inplace=True)
        return self.df

# Usage
# loader = DataLoader('train.csv')
# df = loader.load_data()
# df = loader.handle_missing_values()
```

### Create `src/preprocessor.py`
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class Preprocessor:
    def __init__(self, df):
        self.df = df
        self.label_encoders = {}
        self.preprocessor = None
    
    def identify_columns(self):
        """Identify categorical and numerical columns"""
        self.categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        self.numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Remove target column
        if 'Credit_Score' in self.categorical_cols:
            self.categorical_cols.remove('Credit_Score')
        if 'Credit_Score' in self.numeric_cols:
            self.numeric_cols.remove('Credit_Score')
        
        return self.categorical_cols, self.numeric_cols
    
    def create_preprocessor(self):
        """Create sklearn preprocessing pipeline"""
        self.preprocessor = ColumnTransformer([
            ('num', StandardScaler(), self.numeric_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
             self.categorical_cols)
        ], remainder='drop')
        
        return self.preprocessor
    
    def fit_transform(self, X):
        """Fit and transform data"""
        return self.preprocessor.fit_transform(X)
    
    def transform(self, X):
        """Transform new data"""
        return self.preprocessor.transform(X)

# Usage
# processor = Preprocessor(df)
# processor.identify_columns()
# processor.create_preprocessor()
```

### Create `src/models.py`
```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

class ModelFactory:
    @staticmethod
    def get_logistic_regression():
        return LogisticRegression(max_iter=1000, random_state=42)
    
    @staticmethod
    def get_random_forest():
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    
    @staticmethod
    def get_xgboost():
        return XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='mlogloss'
        )

class ModelTuner:
    def __init__(self, model, X_train, y_train):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
    
    def tune_random_forest(self):
        """Hyperparameter tuning for Random Forest"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 15, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        grid_search = GridSearchCV(
            self.model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
        )
        grid_search.fit(self.X_train, self.y_train)
        
        print(f"Best Parameters: {grid_search.best_params_}")
        print(f"Best Score: {grid_search.best_score_}")
        
        return grid_search.best_estimator_

# Usage
# rf = ModelFactory.get_random_forest()
# tuner = ModelTuner(rf, X_train, y_train)
# best_rf = tuner.tune_random_forest()
```

### Create `src/evaluator.py`
```python
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self, y_true, y_pred, class_names):
        self.y_true = y_true
        self.y_pred = y_pred
        self.class_names = class_names
    
    def get_metrics(self):
        """Calculate all metrics"""
        metrics = {
            'Accuracy': accuracy_score(self.y_true, self.y_pred),
            'Precision': precision_score(self.y_true, self.y_pred, average='weighted'),
            'Recall': recall_score(self.y_true, self.y_pred, average='weighted'),
            'F1-Score': f1_score(self.y_true, self.y_pred, average='weighted')
        }
        return metrics
    
    def print_report(self):
        """Print detailed classification report"""
        print("Classification Report:")
        print(classification_report(self.y_true, self.y_pred, 
                                   target_names=self.class_names))
    
    def plot_confusion_matrix(self, title="Confusion Matrix"):
        """Plot confusion matrix heatmap"""
        cm = confusion_matrix(self.y_true, self.y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names)
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.show()
    
    def get_metrics_dataframe(self):
        """Return metrics as DataFrame"""
        metrics = self.get_metrics()
        return pd.DataFrame(list(metrics.items()), 
                          columns=['Metric', 'Value'])

# Usage
# evaluator = ModelEvaluator(y_test, y_pred, label_encoder.classes_)
# evaluator.print_report()
# evaluator.plot_confusion_matrix()
# metrics_df = evaluator.get_metrics_dataframe()
```

---

## 2️⃣ FEATURE ENGINEERING EXAMPLES

```python
def engineer_features(df):
    """Create new features from existing ones"""
    
    # 1. Financial Ratios
    if 'Monthly_Inhand_Salary' in df.columns and 'Monthly_Income' in df.columns:
        df['Salary_Income_Ratio'] = (
            df['Monthly_Inhand_Salary'] / (df['Monthly_Income'] + 1)
        )
    
    # 2. Debt Indicators
    if 'Outstanding_Debt' in df.columns and 'Credit_Utilization_Ratio' in df.columns:
        df['Debt_Level'] = df['Outstanding_Debt'] * df['Credit_Utilization_Ratio']
    
    # 3. Payment Consistency
    if 'Payment_of_Min_Amount' in df.columns:
        df['Payment_Consistency'] = (
            df['Payment_of_Min_Amount'].map(
                {'Yes': 1, 'No': 0, 'NM': 0}
            )
        )
    
    # 4. Credit History Length (if Age is available)
    if 'Age' in df.columns:
        df['Credit_Experience_Years'] = df['Age'] - 18  # Approximate
    
    # 5. Interaction Features
    if 'Annual_Income' in df.columns and 'Outstanding_Debt' in df.columns:
        df['Debt_to_Income_Ratio'] = (
            df['Outstanding_Debt'] / (df['Annual_Income'] + 1)
        )
    
    return df
```

---

## 3️⃣ HYPERPARAMETER TUNING EXAMPLE

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# Random Forest Hyperparameter Tuning
rf_params = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [10, 15, 20, 25],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    rf_params,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV Score: {grid_search.best_score_:.4f}")

best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)
print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
```

---

## 4️⃣ CROSS-VALIDATION EXAMPLE

```python
from sklearn.model_selection import StratifiedKFold, cross_validate

# Stratified K-Fold with multiple scoring metrics
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scoring = {
    'accuracy': 'accuracy',
    'precision_weighted': 'precision_weighted',
    'recall_weighted': 'recall_weighted',
    'f1_weighted': 'f1_weighted'
}

cv_results = cross_validate(
    best_model, X_train, y_train,
    cv=skf, scoring=scoring, return_train_score=True
)

# Display results
cv_df = pd.DataFrame(cv_results)
print(cv_df[['test_accuracy', 'test_precision_weighted', 
            'test_recall_weighted', 'test_f1_weighted']])

print(f"\nMean Test Accuracy: {cv_results['test_accuracy'].mean():.4f} "
      f"(± {cv_results['test_accuracy'].std():.4f})")
```

---

## 5️⃣ FEATURE IMPORTANCE VISUALIZATION

```python
import matplotlib.pyplot as plt

# For Random Forest
feature_names = (
    list(processor.numeric_cols) + 
    list(processor.categorical_cols)
)

feature_importance = pd.DataFrame({
    'Feature': feature_names,
    'Importance': best_rf.feature_importances_
}).sort_values('Importance', ascending=False).head(15)

plt.figure(figsize=(10, 6))
plt.barh(feature_importance['Feature'], feature_importance['Importance'])
plt.xlabel('Importance')
plt.title('Top 15 Feature Importances - Random Forest')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
```

---

## 6️⃣ MODEL COMPARISON TABLE

```python
# Train all models and compare
results = []

models_dict = {
    'Logistic Regression': ModelFactory.get_logistic_regression(),
    'Random Forest': ModelFactory.get_random_forest(),
    'XGBoost': ModelFactory.get_xgboost()
}

for name, model in models_dict.items():
    # Create pipeline
    pipe = Pipeline([
        ('preprocessor', processor.create_preprocessor()),
        ('model', model)
    ])
    
    # Train
    pipe.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipe.predict(X_test)
    
    results.append({
        'Model': name,
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred, average='weighted'),
        'Recall': recall_score(y_test, y_pred, average='weighted'),
        'F1-Score': f1_score(y_test, y_pred, average='weighted')
    })

comparison_df = pd.DataFrame(results)
print(comparison_df.to_string(index=False))
```

---

## 7️⃣ REQUIREMENTS.TXT

```
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
xgboost==2.0.0
matplotlib==3.7.2
seaborn==0.12.2
jupyter==1.0.0
```

---

## 8️⃣ CONFIG.YAML

```yaml
# Configuration file for the project

# Data
data:
  train_file: 'train.csv'
  test_file: 'test.csv'

# Model Parameters
model:
  random_forest:
    n_estimators: 100
    max_depth: 15
    min_samples_split: 5
    min_samples_leaf: 2
  
  xgboost:
    n_estimators: 100
    learning_rate: 0.1
    max_depth: 6
    subsample: 0.8

# Training
training:
  test_size: 0.2
  random_state: 42
  cv_folds: 5
  stratify: True

# Evaluation
evaluation:
  metrics: ['accuracy', 'precision', 'recall', 'f1']
```

---

**Next Step:** Start with creating the directory structure and implementing the modular code. This alone will make your project stand out in an interview!
