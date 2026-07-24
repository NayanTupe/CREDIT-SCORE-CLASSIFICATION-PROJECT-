# 🎯 Credit Score Classification Project

A complete end-to-end machine learning pipeline for predicting credit scores using multiple classification algorithms.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Models](#models)
- [Results](#results)
- [Contributing](#contributing)

---

## 🎯 Overview

This project builds a machine learning system to **automatically classify credit scores** for financial institutions. Instead of manual credit assessment (slow and error-prone), our model provides fast, consistent, and accurate credit score predictions.

### Key Features
- ✅ **Multiple Models**: Logistic Regression, Random Forest, XGBoost
- ✅ **Hyperparameter Tuning**: GridSearchCV for optimal parameters
- ✅ **Cross-Validation**: 5-fold stratified cross-validation
- ✅ **Feature Engineering**: Automatic feature creation and preprocessing
- ✅ **Comprehensive Evaluation**: Accuracy, Precision, Recall, F1-Score
- ✅ **Production Ready**: Modular, well-documented, scalable code

---

## 📂 Project Structure

```
credit-score-classification/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # Data loading and cleaning
│   ├── preprocessor.py          # Feature engineering and preprocessing
│   ├── models.py                # Model definitions and training
│   ├── evaluator.py             # Evaluation metrics and reporting
│   └── main.py                  # Complete pipeline orchestration
├── notebooks/
│   └── CREDIT SCORE CLASSIFICATION !!!.ipynb  # Jupyter notebook
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── START_HERE.md                # Quick start guide
```

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone the repository** (if applicable)
```bash
git clone <repository-url>
cd credit-score-classification
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### Run the Complete Pipeline

```bash
cd src
python main.py
```

This will:
- Load and clean data
- Engineer features
- Train 3 models
- Perform hyperparameter tuning
- Cross-validate results
- Generate visualizations
- Compare all models

### Expected Output
```
================================================================================
CREDIT SCORE CLASSIFICATION - COMPLETE PIPELINE
================================================================================

STEP 1: LOAD AND CLEAN DATA
✓ Data loaded successfully!
✓ Missing values handled
✓ Duplicates removed

STEP 2: PREPROCESS AND ENGINEER FEATURES
✓ Features engineered
✓ Categorical features encoded
✓ Preprocessor fitted

STEP 3: TRAIN MODELS
✓ Logistic Regression trained
✓ Random Forest trained with hyperparameter tuning
✓ XGBoost trained with hyperparameter tuning

STEP 4: EVALUATE AND COMPARE MODELS
✓ All models evaluated

PIPELINE COMPLETED SUCCESSFULLY!
```

---

## 📖 Usage

### 1. Load and Clean Data

```python
from src.data_loader import DataLoader

# Load data
loader = DataLoader('train.csv')
df = loader.load_data()

# Display information
loader.display_basic_info()

# Clean data
df = loader.handle_missing_values(strategy='mean')
df = loader.remove_duplicates()
```

### 2. Preprocess Features

```python
from src.preprocessor import Preprocessor

# Initialize preprocessor
preprocessor = Preprocessor(df, target_column='Credit_Score')

# Identify columns
preprocessor.identify_columns()

# Engineer features
preprocessor.engineer_features()

# Encode categorical features
preprocessor.encode_categorical_features()

# Get target and features
y, label_encoder, class_names = preprocessor.encode_target()
X = df.drop('Credit_Score', axis=1)

# Fit preprocessor
X_transformed = preprocessor.fit_preprocessor(X)
```

### 3. Train Models

```python
from src.models import ModelFactory, ModelTrainer
from sklearn.model_selection import train_test_split

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_transformed, y, test_size=0.2, random_state=42, stratify=y
)

# Create and train model
model = ModelFactory.get_random_forest()
trainer = ModelTrainer(model, X_train, X_test, y_train, y_test)

# Train
trainer.train()

# Cross-validation
trainer.cross_validate(cv=5)

# Hyperparameter tuning
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 15, 20],
    'min_samples_split': [5, 10]
}
best_model, best_params = trainer.hyperparameter_tuning(param_grid)
```

### 4. Evaluate Models

```python
from src.evaluator import ModelEvaluator

# Make predictions
y_pred = best_model.predict(X_test)

# Evaluate
evaluator = ModelEvaluator(y_test, y_pred, class_names=class_names, model_name='Random Forest')

# Print results
evaluator.print_metrics_summary()
evaluator.print_confusion_matrix()
evaluator.get_per_class_metrics()
evaluator.plot_confusion_matrix()
```

### 5. Compare Models

```python
from src.evaluator import ModelComparison

# Create comparison
comparator = ModelComparison()

# Add multiple models
for model_name in ['Logistic Regression', 'Random Forest', 'XGBoost']:
    y_pred = models[model_name].predict(X_test)
    comparator.add_model_result(model_name, y_test, y_pred)

# Get comparison
comparison_df = comparator.get_comparison_table()
comparator.plot_model_comparison()
```

---

## 🤖 Models

### Logistic Regression
- **Use Case**: Baseline model, interpretable
- **Pros**: Fast, simple, interpretable
- **Cons**: Assumes linear relationships

### Random Forest
- **Use Case**: Default choice for tree-based problems
- **Pros**: Handles non-linearity, feature importance, robust
- **Cons**: Less interpretable than single tree

### XGBoost
- **Use Case**: When highest accuracy is needed
- **Pros**: State-of-the-art, powerful, well-tuned
- **Cons**: More complex, requires careful tuning

---

## 📊 Results

All models are evaluated on:
- **Accuracy**: Overall correctness
- **Precision**: False positive rate
- **Recall**: False negative rate
- **F1-Score**: Balance between precision and recall
- **Confusion Matrix**: Per-class breakdown
- **Cross-Validation**: Model stability

Example Results:
```
Model Comparison
╔═══════════════════════╦══════════╦════════════╦════════╦═══════════╗
║ Model                 ║ Accuracy ║ Precision  ║ Recall ║ F1-Score  ║
╠═══════════════════════╬══════════╬════════════╬════════╬═══════════╣
║ Logistic Regression   ║  0.7850  ║   0.7820   ║ 0.7850 ║   0.7835  ║
║ Random Forest         ║  0.8250  ║   0.8200   ║ 0.8250 ║   0.8225  ║
║ XGBoost               ║  0.8150  ║   0.8100   ║ 0.8150 ║   0.8125  ║
╚═══════════════════════╩══════════╩════════════╩════════╩═══════════╝

Best Model: Random Forest (82.50% Accuracy)
```

---

## 📈 Key Insights

1. **Feature Importance**: Identifies which factors most influence credit scores
2. **Class Distribution**: Shows if model handles imbalanced classes well
3. **Per-Class Performance**: Reveals which credit classes are hardest to predict
4. **Overfitting Analysis**: Cross-validation scores show model generalization

---

## 🔍 Data Requirements

### Input Format
- CSV file with numerical and categorical features
- Target column: Credit Score (Good, Standard, Poor) or similar classes
- Minimum features: 10+
- Minimum samples: 1000+

### Expected Features
- Financial indicators (income, debt, credit utilization)
- Payment history (payment behavior, minimum amount paid)
- Demographics (occupation, age, etc.)
- Loan information (loan type, amount, duration)

---

## 📝 Configuration

Edit `config.yaml` to customize:
- Model hyperparameters
- Training settings
- Feature engineering options
- Evaluation metrics
- Preprocessing strategies

---

## 🎓 Interview Ready

This project demonstrates:
- ✅ Complete ML pipeline design
- ✅ Proper data preprocessing and validation
- ✅ Multiple model comparison
- ✅ Hyperparameter optimization
- ✅ Cross-validation and evaluation
- ✅ Feature engineering
- ✅ Production-ready code structure

---

## 📚 Further Improvements

### Coming Soon
- [ ] Advanced ensemble methods (Stacking, Blending)
- [ ] Deep learning with neural networks
- [ ] SHAP model explanation
- [ ] Feature selection optimization
- [ ] Model deployment with API
- [ ] Real-time prediction service

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [your-profile](https://linkedin.com/in/your-profile)

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: your-email@example.com

---

## 🙏 Acknowledgments

- sklearn, pandas, numpy teams
- XGBoost developers
- Open source community

---

**Last Updated**: June 2024
**Version**: 1.0.0
