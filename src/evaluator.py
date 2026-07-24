"""
Model Evaluation Module
Handles evaluation metrics, confusion matrix, and performance reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve, auc
)


class ModelEvaluator:
    """Evaluate model performance"""
    
    def __init__(self, y_true, y_pred, y_pred_proba=None, class_names=None, model_name="Model"):
        """
        Initialize ModelEvaluator
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (for ROC-AUC)
            class_names: List of class names
            model_name: Name of the model
        """
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_pred_proba = y_pred_proba
        self.class_names = class_names if class_names is not None else [f'Class_{i}' for i in np.unique(y_true)]
        self.model_name = model_name
        self.metrics = {}
    
    def calculate_metrics(self):
        """
        Calculate all evaluation metrics
        
        Returns:
            dict: Dictionary of all metrics
        """
        self.metrics = {
            'Accuracy': accuracy_score(self.y_true, self.y_pred),
            'Precision (Weighted)': precision_score(self.y_true, self.y_pred, average='weighted', zero_division=0),
            'Recall (Weighted)': recall_score(self.y_true, self.y_pred, average='weighted', zero_division=0),
            'F1-Score (Weighted)': f1_score(self.y_true, self.y_pred, average='weighted', zero_division=0)
        }
        
        # Per-class metrics
        self.metrics['Precision (Macro)'] = precision_score(self.y_true, self.y_pred, average='macro', zero_division=0)
        self.metrics['Recall (Macro)'] = recall_score(self.y_true, self.y_pred, average='macro', zero_division=0)
        self.metrics['F1-Score (Macro)'] = f1_score(self.y_true, self.y_pred, average='macro', zero_division=0)
        
        return self.metrics
    
    def print_metrics_summary(self):
        """Print metrics summary in formatted table"""
        if not self.metrics:
            self.calculate_metrics()
        
        print(f"\n{'='*60}")
        print(f"EVALUATION METRICS - {self.model_name}")
        print(f"{'='*60}")
        
        metrics_df = pd.DataFrame(list(self.metrics.items()), 
                                 columns=['Metric', 'Value'])
        metrics_df['Value'] = metrics_df['Value'].apply(lambda x: f'{x:.4f}')
        
        print(metrics_df.to_string(index=False))
        
        return metrics_df
    
    def print_classification_report(self):
        """Print detailed classification report"""
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION REPORT - {self.model_name}")
        print(f"{'='*60}\n")
        
        report = classification_report(
            self.y_true, self.y_pred,
            target_names=self.class_names,
            digits=4
        )
        print(report)
        
        return report
    
    def get_confusion_matrix(self):
        """
        Get confusion matrix
        
        Returns:
            ndarray: Confusion matrix
        """
        return confusion_matrix(self.y_true, self.y_pred)
    
    def print_confusion_matrix(self):
        """Print confusion matrix as formatted table"""
        cm = self.get_confusion_matrix()
        
        print(f"\n{'='*60}")
        print(f"CONFUSION MATRIX - {self.model_name}")
        print(f"{'='*60}\n")
        
        cm_df = pd.DataFrame(
            cm,
            index=[f'Actual_{c}' for c in self.class_names],
            columns=[f'Predicted_{c}' for c in self.class_names]
        )
        print(cm_df)
        
        return cm_df
    
    def plot_confusion_matrix(self, figsize=(8, 6), save_path=None):
        """
        Plot confusion matrix heatmap
        
        Args:
            figsize (tuple): Figure size
            save_path (str): Path to save figure
        """
        cm = self.get_confusion_matrix()
        
        plt.figure(figsize=figsize)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names,
                   cbar_kws={'label': 'Count'})
        
        plt.title(f'Confusion Matrix - {self.model_name}', fontsize=14, weight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def get_per_class_metrics(self):
        """
        Get per-class precision, recall, F1-score
        
        Returns:
            DataFrame: Per-class metrics
        """
        from sklearn.metrics import precision_recall_fscore_support
        
        precision, recall, f1, support = precision_recall_fscore_support(
            self.y_true, self.y_pred, zero_division=0
        )
        
        per_class_df = pd.DataFrame({
            'Class': self.class_names,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1,
            'Support': support
        })
        
        print(f"\n{'='*60}")
        print(f"PER-CLASS METRICS - {self.model_name}")
        print(f"{'='*60}\n")
        print(per_class_df.to_string(index=False))
        
        return per_class_df
    
    def plot_roc_curve(self, figsize=(8, 6), save_path=None):
        """
        Plot ROC curve (for binary classification)
        
        Args:
            figsize (tuple): Figure size
            save_path (str): Path to save figure
        """
        if self.y_pred_proba is None or len(np.unique(self.y_true)) != 2:
            print("ROC curve requires binary classification and probability predictions")
            return
        
        # Calculate ROC curve
        fpr, tpr, thresholds = roc_curve(self.y_true, self.y_pred_proba[:, 1])
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=figsize)
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {self.model_name}', fontsize=14, weight='bold')
        plt.legend(loc="lower right")
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


class ModelComparison:
    """Compare multiple models"""
    
    def __init__(self):
        """Initialize ModelComparison"""
        self.results = []
    
    def add_model_result(self, model_name, y_true, y_pred):
        """
        Add model evaluation result
        
        Args:
            model_name (str): Name of the model
            y_true: True labels
            y_pred: Predicted labels
        """
        evaluator = ModelEvaluator(y_true, y_pred, class_names=None, model_name=model_name)
        metrics = evaluator.calculate_metrics()
        
        result = {'Model': model_name, **metrics}
        self.results.append(result)
    
    def get_comparison_table(self):
        """
        Get comparison table of all models
        
        Returns:
            DataFrame: Comparison table
        """
        if not self.results:
            print("No results to compare. Add models using add_model_result()")
            return None
        
        comparison_df = pd.DataFrame(self.results)
        
        print(f"\n{'='*80}")
        print("MODEL COMPARISON")
        print(f"{'='*80}\n")
        
        # Format for display
        display_df = comparison_df.copy()
        for col in display_df.columns:
            if col != 'Model':
                display_df[col] = display_df[col].apply(lambda x: f'{x:.4f}')
        
        print(display_df.to_string(index=False))
        
        return comparison_df
    
    def plot_model_comparison(self, figsize=(12, 6), save_path=None):
        """
        Plot comparison of models
        
        Args:
            figsize (tuple): Figure size
            save_path (str): Path to save figure
        """
        if not self.results or len(self.results) < 2:
            print("Need at least 2 models to compare")
            return
        
        comparison_df = pd.DataFrame(self.results)
        
        # Plot accuracy comparison
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Accuracy
        axes[0].bar(comparison_df['Model'], comparison_df['Accuracy'], color='steelblue')
        axes[0].set_title('Accuracy Comparison', fontsize=12, weight='bold')
        axes[0].set_ylabel('Accuracy', fontsize=11)
        axes[0].set_ylim([0, 1])
        for i, v in enumerate(comparison_df['Accuracy']):
            axes[0].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=10)
        axes[0].tick_params(axis='x', rotation=45)
        
        # F1-Score
        axes[1].bar(comparison_df['Model'], comparison_df['F1-Score (Weighted)'], color='coral')
        axes[1].set_title('F1-Score Comparison', fontsize=12, weight='bold')
        axes[1].set_ylabel('F1-Score', fontsize=11)
        axes[1].set_ylim([0, 1])
        for i, v in enumerate(comparison_df['F1-Score (Weighted)']):
            axes[1].text(i, v + 0.02, f'{v:.4f}', ha='center', fontsize=10)
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


# Example usage
if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Create sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15,
                              n_classes=3, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Evaluate
    evaluator = ModelEvaluator(y_test, y_pred, class_names=['Class_0', 'Class_1', 'Class_2'])
    evaluator.print_metrics_summary()
    evaluator.print_confusion_matrix()
    evaluator.get_per_class_metrics()
    evaluator.plot_confusion_matrix()
