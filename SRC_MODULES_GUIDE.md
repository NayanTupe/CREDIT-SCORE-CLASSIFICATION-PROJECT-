# 🚀 HOW TO USE THE SRC/ MODULES - COMPLETE GUIDE

---

## 📚 OVERVIEW

You now have 5 professional Python modules ready to use:

```
src/
├── data_loader.py       → Load and clean data
├── preprocessor.py      → Feature engineering & encoding
├── models.py            → Create and train models
├── evaluator.py         → Evaluate and compare models
└── main.py              → Complete pipeline (use this!)
```

---

## ⚡ QUICKEST START (Just Run This)

```bash
cd src
python main.py
```

That's it! Everything runs automatically. This will:
1. Load your data
2. Clean it
3. Engineer features
4. Train 3 models
5. Tune hyperparameters
6. Compare results

---

## 📖 DETAILED USAGE GUIDE

### Option 1: Use the Complete Pipeline (RECOMMENDED)

```python
# src/main.py
from main import CreditScoringPipeline

# Initialize
pipeline = CreditScoringPipeline(
    data_path='train.csv',
    target_column='Credit_Score',
    test_size=0.2,
    random_state=42
)

# Run everything
pipeline.run_pipeline(tune_hyperparameters=True, cv_folds=5)

# Visualize results
pipeline.visualize_results()

# Get best model
best_name, best_model = pipeline.get_best_model()
```

### Option 2: Use Individual Modules

#### Step 1: Load Data

```python
from data_loader import DataLoader

loader = DataLoader('train.csv')
df = loader.load_data()

# Check data
loader.display_basic_info()

# Clean data
df = loader.handle_missing_values(strategy='mean')
df = loader.remove_duplicates()

print(f"Cleaned data shape: {df.shape}")
```

#### Step 2: Preprocess Features

```python
from preprocessor import Preprocessor

preprocessor = Preprocessor(df, target_column='Credit_Score')

# Identify columns automatically
preprocessor.identify_columns()

# Create new features
preprocessor.engineer_features()

# Encode categories
preprocessor.encode_categorical_features()

# Prepare target
y, label_encoder, class_names = preprocessor.encode_target()
print(f"Classes: {class_names}")

# Get features
X = df.drop('Credit_Score', axis=1)

# Transform data
X_transformed = preprocessor.fit_preprocessor(X)
feature_names = preprocessor.get_feature_names()

print(f"Features after preprocessing: {X_transformed.shape[1]}")
```

#### Step 3: Split Data

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_transformed, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # Important for classification!
)

print(f"Train: {X_train.shape} | Test: {X_test.shape}")
```

#### Step 4: Train Models

```python
from models import ModelFactory, ModelTrainer

# Option A: Simple Training
model = ModelFactory.get_random_forest()
trainer = ModelTrainer(model, X_train, X_test, y_train, y_test)
trainer.train()

# Option B: With Cross-Validation
cv_results = trainer.cross_validate(cv=5)

# Option C: With Hyperparameter Tuning
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 15, 20],
    'min_samples_split': [5, 10]
}

best_model, best_params = trainer.hyperparameter_tuning(param_grid, cv=5)
print(f"Best params: {best_params}")
```

#### Step 5: Evaluate Models

```python
from evaluator import ModelEvaluator, ModelComparison

# Evaluate single model
y_pred = best_model.predict(X_test)
evaluator = ModelEvaluator(y_test, y_pred, class_names=class_names, 
                          model_name='Random Forest')

# Print results
evaluator.print_metrics_summary()
evaluator.print_confusion_matrix()
evaluator.get_per_class_metrics()
evaluator.plot_confusion_matrix()

# Compare multiple models
comparator = ModelComparison()

for name in ['Logistic Regression', 'Random Forest', 'XGBoost']:
    model = get_model(name)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    comparator.add_model_result(name, y_test, y_pred)

# View comparison
comparison_table = comparator.get_comparison_table()
comparator.plot_model_comparison()
```

---

## 🎯 COMMON USE CASES

### Use Case 1: Quick Model Training

```python
from main import CreditScoringPipeline

pipeline = CreditScoringPipeline('train.csv')
pipeline.run_pipeline(tune_hyperparameters=True)
```

### Use Case 2: Just Evaluate Existing Model

```python
from data_loader import DataLoader
from preprocessor import Preprocessor
from evaluator import ModelEvaluator
import pickle

# Load data
loader = DataLoader('train.csv')
df = loader.load_data()

# Preprocess
preprocessor = Preprocessor(df)
preprocessor.identify_columns()
preprocessor.encode_categorical_features()
y, le, classes = preprocessor.encode_target()
X = df.drop('Credit_Score', axis=1)
X_test = preprocessor.fit_preprocessor(X)

# Load saved model
with open('trained_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Evaluate
y_pred = model.predict(X_test)
evaluator = ModelEvaluator(y_test, y_pred, class_names=classes)
evaluator.print_metrics_summary()
```

### Use Case 3: Compare Models Only

```python
from evaluator import ModelComparison
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

comparator = ModelComparison()

# Add results from your models
models = {
    'LR': LogisticRegression(),
    'RF': RandomForestClassifier(),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    comparator.add_model_result(name, y_test, y_pred)

# Get comparison
comparator.get_comparison_table()
comparator.plot_model_comparison()
```

### Use Case 4: Feature Engineering Only

```python
from preprocessor import Preprocessor

preprocessor = Preprocessor(df)
preprocessor.identify_columns()
preprocessor.engineer_features()

new_df = preprocessor.get_processed_data()
# Now you have engineered features to use elsewhere
```

---

## 📊 PARAMETER EXPLANATIONS

### DataLoader

```python
loader = DataLoader('train.csv')

# Load data
loader.load_data()  # Read CSV

# Clean data
loader.handle_missing_values(strategy='mean')  # 'mean', 'median', 'mode'
loader.remove_duplicates()
loader.remove_outliers(method='iqr', threshold=1.5)

# Check data
loader.display_basic_info()  # Shows stats
summary = loader.get_data_summary()  # Returns dict
```

### Preprocessor

```python
preprocessor = Preprocessor(df, target_column='Credit_Score')

# Setup
preprocessor.identify_columns()

# Feature engineering
preprocessor.engineer_features()

# Encoding
preprocessor.encode_categorical_features()
y, encoder, classes = preprocessor.encode_target()

# Fit pipeline
X_transformed = preprocessor.fit_preprocessor(X)

# Get names
feature_names = preprocessor.get_feature_names()
```

### ModelFactory

```python
from models import ModelFactory

# Get pre-configured models
lr = ModelFactory.get_logistic_regression()
rf = ModelFactory.get_random_forest(n_estimators=100)
xgb = ModelFactory.get_xgboost(n_estimators=100)
```

### ModelTrainer

```python
trainer = ModelTrainer(model, X_train, X_test, y_train, y_test)

# Train
trainer.train()

# Validate
trainer.cross_validate(cv=5)

# Optimize
best_model, params = trainer.hyperparameter_tuning(
    param_grid={'n_estimators': [100, 200]},
    cv=5
)

# Feature importance
importance_df = trainer.get_feature_importance(feature_names)
```

### ModelEvaluator

```python
evaluator = ModelEvaluator(y_test, y_pred, 
                          y_pred_proba=None,
                          class_names=['Good', 'Standard', 'Poor'],
                          model_name='Random Forest')

# Evaluate
metrics = evaluator.calculate_metrics()
evaluator.print_metrics_summary()
evaluator.print_classification_report()
evaluator.print_confusion_matrix()
evaluator.get_per_class_metrics()

# Visualize
evaluator.plot_confusion_matrix()
evaluator.plot_roc_curve()
```

---

## ⚠️ IMPORTANT NOTES

### Data Path
Change this to your actual CSV file:
```python
pipeline = CreditScoringPipeline(data_path='train.csv')
```

### Target Column
Specify your target column name:
```python
preprocessor = Preprocessor(df, target_column='Credit_Score')
```

### Stratified Split
Always use `stratify=y` for classification:
```python
train_test_split(X, y, stratify=y, ...)
```

### Feature Names
After preprocessing, get feature names:
```python
feature_names = preprocessor.get_feature_names()
```

---

## 🐛 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'sklearn'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Error: "No such file or directory: 'train.csv'"
**Solution**: Check file path and name
```python
pipeline = CreditScoringPipeline(data_path='/full/path/to/train.csv')
```

### Error: "Could not convert to numeric"
**Solution**: Check your data types
```python
loader.display_basic_info()  # Shows data types
```

### Warning: "Column not found"
**Solution**: Check column names match
```python
print(df.columns)  # See all columns
```

---

## 💾 SAVING AND LOADING MODELS

### Save Model

```python
import pickle

# After training
with open('my_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
```

### Load Model

```python
import pickle

with open('my_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Use loaded model
y_pred = loaded_model.predict(X_test)
```

---

## 🎓 BEST PRACTICES

1. **Always use stratified split** for classification
2. **Always cross-validate** before claiming good results
3. **Always tune hyperparameters** on training data only
4. **Always evaluate on separate test set**
5. **Always save your best model**
6. **Always document your choices**

---

## 📝 EXAMPLE: COMPLETE WORKFLOW

```python
# 1. Load data
from data_loader import DataLoader
loader = DataLoader('train.csv')
df = loader.load_data()
df = loader.handle_missing_values()
df = loader.remove_duplicates()

# 2. Preprocess
from preprocessor import Preprocessor
prep = Preprocessor(df)
prep.identify_columns()
prep.engineer_features()
prep.encode_categorical_features()
y, le, classes = prep.encode_target()
X = df.drop('Credit_Score', axis=1)
X_transformed = prep.fit_preprocessor(X)

# 3. Split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X_transformed, y, test_size=0.2, stratify=y, random_state=42
)

# 4. Train
from models import ModelFactory, ModelTrainer
model = ModelFactory.get_random_forest()
trainer = ModelTrainer(model, X_train, X_test, y_train, y_test)
trainer.train()
trainer.cross_validate(cv=5)

# 5. Optimize (optional)
param_grid = {'n_estimators': [100, 200], 'max_depth': [10, 15, 20]}
best_model, params = trainer.hyperparameter_tuning(param_grid)

# 6. Evaluate
from evaluator import ModelEvaluator
y_pred = best_model.predict(X_test)
evaluator = ModelEvaluator(y_test, y_pred, class_names=classes)
evaluator.print_metrics_summary()
evaluator.plot_confusion_matrix()

# 7. Save
import pickle
with open('best_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print("✓ Pipeline completed successfully!")
```

---

**That's it! You now have production-ready ML code. Start with `main.py` for the easiest experience.** 🚀
