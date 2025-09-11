import math
from typing import List, Dict, Union, Optional, Any
import numpy as np


class DConfusion:
    """
    A comprehensive confusion matrix class for both binary and multi-class classification analysis.
    
    This class can handle:
    1. Binary classification using individual TP, FN, FP, TN values
    2. Multi-class classification using a confusion matrix or predictions
    
    Args:
        For binary classification:
            true_positive (int): Number of true positive predictions
            false_negative (int): Number of false negative predictions  
            false_positive (int): Number of false positive predictions
            true_negative (int): Number of true negative predictions
            
        For multi-class classification:
            confusion_matrix (List[List[int]] or np.ndarray): NxN confusion matrix
            labels (List): Optional list of class labels
            
    Raises:
        ValueError: If any input value is negative or matrix dimensions don't match
        TypeError: If any input value is not a number
    """

    def __init__(self, true_positive: Optional[int] = None, false_negative: Optional[int] = None, 
                 false_positive: Optional[int] = None, true_negative: Optional[int] = None,
                 confusion_matrix: Optional[Union[List[List[int]], np.ndarray]] = None,
                 labels: Optional[List[Any]] = None):
        
        # Determine if this is binary or multi-class based on inputs
        if confusion_matrix is not None:
            self._init_multiclass(confusion_matrix, labels)
        elif all(v is not None for v in [true_positive, false_negative, false_positive, true_negative]):
            self._init_binary(true_positive, false_negative, false_positive, true_negative)
        else:
            raise ValueError("Either provide (tp, fn, fp, tn) for binary classification or confusion_matrix for multi-class")
    
    def _init_binary(self, true_positive: int, false_negative: int, false_positive: int, true_negative: int):
        """Initialize for binary classification."""
        # Input validation
        values = [true_positive, false_negative, false_positive, true_negative]
        names = ['true_positive', 'false_negative', 'false_positive', 'true_negative']
        
        for value, name in zip(values, names):
            if not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number, got {type(value).__name__}")
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")
        
        self.is_binary = True
        self.true_positive = int(true_positive)
        self.false_positive = int(false_positive)
        self.true_negative = int(true_negative)
        self.false_negative = int(false_negative)
        self.total = self.true_positive + self.false_negative + self.false_positive + self.true_negative
        
        # Create 2x2 matrix representation
        self.matrix = np.array([[self.true_positive, self.false_positive],
                               [self.false_negative, self.true_negative]])
        self.labels = [0, 1]  # Default binary labels
        self.n_classes = 2

    def _init_multiclass(self, confusion_matrix: Union[List[List[int]], np.ndarray], labels: Optional[List[Any]] = None):
        """Initialize for multi-class classification."""
        self.is_binary = False
        
        # Convert to numpy array
        self.matrix = np.array(confusion_matrix)
        
        # Validation
        if len(self.matrix.shape) != 2:
            raise ValueError("Confusion matrix must be 2-dimensional")
        if self.matrix.shape[0] != self.matrix.shape[1]:
            raise ValueError("Confusion matrix must be square")
        if np.any(self.matrix < 0):
            raise ValueError("All values in confusion matrix must be non-negative")
        
        self.n_classes = self.matrix.shape[0]
        self.total = int(np.sum(self.matrix))
        
        # Set labels
        if labels is None:
            self.labels = list(range(self.n_classes))
        else:
            if len(labels) != self.n_classes:
                raise ValueError(f"Number of labels ({len(labels)}) must match matrix size ({self.n_classes})")
            self.labels = list(labels)
        
        # For binary case, also set individual values for backward compatibility
        if self.n_classes == 2:
            self.true_positive = int(self.matrix[1, 1])
            self.false_positive = int(self.matrix[0, 1])
            self.true_negative = int(self.matrix[0, 0])
            self.false_negative = int(self.matrix[1, 0])

    def __str__(self) -> str:
        """String representation of the confusion matrix."""
        if self.is_binary and self.n_classes == 2:
            return (
                f"Confusion Matrix:\n"
                f"                 \t Predicted Positive  Predicted Negative\n"
                f"Actual Positive  \t{self.true_positive:^18}  {self.false_negative:^18}\n"
                f"Actual Negative  \t{self.false_positive:^18}  {self.true_negative:^18}"
            )
        else:
            return self._format_multiclass_matrix()
    
    def _format_multiclass_matrix(self) -> str:
        """Format multi-class confusion matrix for display."""
        # Calculate column widths
        max_label_width = max(len(str(label)) for label in self.labels)
        max_value_width = max(len(str(val)) for val in self.matrix.flatten())
        col_width = max(max_label_width, max_value_width, 8) + 2
        
        result = "Confusion Matrix:\n"
        
        # Header row
        result += "True\\Pred".ljust(max_label_width + 2)
        for label in self.labels:
            result += str(label).center(col_width)
        result += "\n"
        
        # Data rows
        for i, true_label in enumerate(self.labels):
            result += str(true_label).ljust(max_label_width + 2)
            for j in range(self.n_classes):
                result += str(self.matrix[i, j]).center(col_width)
            result += "\n"
        
        return result.rstrip()

    def __repr__(self) -> str:
        """Detailed representation of the DConfusion object."""
        if self.is_binary and self.n_classes == 2:
            return (f"DConfusion(true_positive={self.true_positive}, "
                    f"false_negative={self.false_negative}, "
                    f"false_positive={self.false_positive}, "
                    f"true_negative={self.true_negative})")
        else:
            return f"DConfusion(confusion_matrix={self.matrix.tolist()}, labels={self.labels})"

    def __eq__(self, other) -> bool:
        """Check equality with another DConfusion object."""
        if not isinstance(other, DConfusion):
            return False
        return (np.array_equal(self.matrix, other.matrix) and 
                self.labels == other.labels)

    @staticmethod
    def _validate_non_zero_denominator(denominator: float, metric_name: str) -> None:
        """Helper method to validate denominators for metric calculations."""
        if denominator == 0:
            raise ZeroDivisionError(f"Cannot calculate {metric_name}: denominator is zero")

    def frequency(self) -> str:
        """
        Calculate and return frequency percentages for each cell.
        
        Returns:
            str: Formatted string showing frequency percentages
            
        Raises:
            ZeroDivisionError: If total is zero
        """
        if self.total == 0:
            raise ZeroDivisionError("Cannot calculate frequency for an empty confusion matrix")

        if self.is_binary and self.n_classes == 2:
            tp_freq = (self.true_positive / self.total) * 100
            tn_freq = (self.true_negative / self.total) * 100
            fp_freq = (self.false_positive / self.total) * 100
            fn_freq = (self.false_negative / self.total) * 100

            return (
                f"Confusion Matrix Frequency (%):\n"
                f"                 \t Predicted Positive  Predicted Negative\n"
                f"Actual Positive  \t{tp_freq:^18.2f}  {fn_freq:^18.2f}\n"
                f"Actual Negative  \t{fp_freq:^18.2f}  {tn_freq:^18.2f}"
            )
        else:
            return self._format_multiclass_frequency()
    
    def _format_multiclass_frequency(self) -> str:
        """Format multi-class frequency matrix for display."""
        freq_matrix = (self.matrix / self.total) * 100
        
        max_label_width = max(len(str(label)) for label in self.labels)
        col_width = 10
        
        result = "Confusion Matrix Frequency (%):\n"
        
        # Header row
        result += "True\\Pred".ljust(max_label_width + 2)
        for label in self.labels:
            result += str(label).center(col_width)
        result += "\n"
        
        # Data rows
        for i, true_label in enumerate(self.labels):
            result += str(true_label).ljust(max_label_width + 2)
            for j in range(self.n_classes):
                result += f"{freq_matrix[i, j]:.2f}".center(col_width)
            result += "\n"
        
        return result.rstrip()

    def get_sum_of_all(self) -> int:
        """Get total number of samples."""
        return self.total

    def get_confusion_matrix(self) -> List[List[int]]:
        """
        Get confusion matrix as a 2D list.
        
        Returns:
            List[List[int]]: NxN matrix
        """
        return self.matrix.tolist()

    def get_sum_of_errors(self) -> int:
        """Get total number of incorrect predictions."""
        return self.total - int(np.trace(self.matrix))

    def get_sum_of_corrects(self) -> int:
        """Get total number of correct predictions."""
        return int(np.trace(self.matrix))

    def get_accuracy(self) -> float:
        """
        Calculate overall accuracy.
        
        Returns:
            float: Accuracy value between 0 and 1
        """
        self._validate_non_zero_denominator(self.total, "accuracy")
        return np.trace(self.matrix) / self.total

    # Alias for accuracy
    get_ccr = get_accuracy

    def get_error_rate(self) -> float:
        """Calculate overall error rate."""
        return 1 - self.get_accuracy()

    def get_class_metrics(self, class_index: Optional[int] = None, class_label: Optional[Any] = None) -> Dict[str, float]:
        """
        Get metrics for a specific class in multi-class setting.
        
        Args:
            class_index: Index of the class (0-based)
            class_label: Label of the class
            
        Returns:
            Dict with precision, recall, f1_score, specificity for the class
        """
        if class_label is not None:
            if class_label not in self.labels:
                raise ValueError(f"Class label '{class_label}' not found in {self.labels}")
            class_index = self.labels.index(class_label)
        elif class_index is None:
            raise ValueError("Either class_index or class_label must be provided")
        
        if not 0 <= class_index < self.n_classes:
            raise ValueError(f"class_index must be between 0 and {self.n_classes-1}")
        
        # Calculate TP, FP, FN, TN for this class
        tp = self.matrix[class_index, class_index]
        fp = np.sum(self.matrix[:, class_index]) - tp
        fn = np.sum(self.matrix[class_index, :]) - tp
        tn = self.total - tp - fp - fn
        
        metrics = {}
        
        # Precision
        try:
            metrics['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        except:
            metrics['precision'] = 0.0
            
        # Recall
        try:
            metrics['recall'] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        except:
            metrics['recall'] = 0.0
            
        # F1 Score
        if metrics['precision'] + metrics['recall'] > 0:
            metrics['f1_score'] = 2 * metrics['precision'] * metrics['recall'] / (metrics['precision'] + metrics['recall'])
        else:
            metrics['f1_score'] = 0.0
            
        # Specificity
        try:
            metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        except:
            metrics['specificity'] = 0.0
        
        return metrics

    def get_macro_metrics(self) -> Dict[str, float]:
        """Calculate macro-averaged metrics across all classes."""
        all_metrics = []
        
        for i in range(self.n_classes):
            class_metrics = self.get_class_metrics(class_index=i)
            all_metrics.append(class_metrics)
        
        # Calculate macro averages
        macro_metrics = {}
        for metric in ['precision', 'recall', 'f1_score', 'specificity']:
            values = [m[metric] for m in all_metrics if not math.isnan(m[metric])]
            macro_metrics[f'macro_{metric}'] = sum(values) / len(values) if values else 0.0
        
        return macro_metrics

    def get_weighted_metrics(self) -> Dict[str, float]:
        """Calculate weighted-averaged metrics across all classes."""
        all_metrics = []
        class_support = []
        
        for i in range(self.n_classes):
            class_metrics = self.get_class_metrics(class_index=i)
            all_metrics.append(class_metrics)
            # Support is the number of true instances for this class
            class_support.append(np.sum(self.matrix[i, :]))
        
        # Calculate weighted averages
        weighted_metrics = {}
        total_support = sum(class_support)
        
        for metric in ['precision', 'recall', 'f1_score', 'specificity']:
            weighted_sum = sum(m[metric] * support for m, support in zip(all_metrics, class_support)
                             if not math.isnan(m[metric]))
            weighted_metrics[f'weighted_{metric}'] = weighted_sum / total_support if total_support > 0 else 0.0
        
        return weighted_metrics

    # Binary classification methods (work for binary case or when n_classes=2)
    def get_recall(self) -> float:
        """Calculate recall for binary classification or positive class."""
        if not hasattr(self, 'true_positive'):
            # Use class 1 (positive class) for multi-class
            return self.get_class_metrics(class_index=1)['recall']
        
        denominator = self.true_positive + self.false_negative
        self._validate_non_zero_denominator(denominator, "recall")
        return self.true_positive / denominator

    def get_precision(self) -> float:
        """Calculate precision for binary classification or positive class."""
        if not hasattr(self, 'true_positive'):
            # Use class 1 (positive class) for multi-class
            return self.get_class_metrics(class_index=1)['precision']
            
        denominator = self.true_positive + self.false_positive
        self._validate_non_zero_denominator(denominator, "precision")
        return self.true_positive / denominator

    def get_f1_score(self) -> float:
        """Calculate F1 score for binary classification or positive class."""
        if not hasattr(self, 'true_positive'):
            # Use class 1 (positive class) for multi-class
            return self.get_class_metrics(class_index=1)['f1_score']
            
        precision = self.get_precision()
        recall = self.get_recall()
        denominator = precision + recall
        self._validate_non_zero_denominator(denominator, "F1 score")
        return 2 * precision * recall / denominator

    def get_specificity(self) -> float:
        """Calculate specificity for binary classification or negative class."""
        if not hasattr(self, 'true_negative'):
            # Use class 0 (negative class) for multi-class
            return self.get_class_metrics(class_index=0)['specificity']
            
        denominator = self.true_negative + self.false_positive
        self._validate_non_zero_denominator(denominator, "specificity")
        return self.true_negative / denominator

    # Aliases for backward compatibility
    get_true_positive_rate = get_recall
    get_sensitivity = get_recall
    get_probability_of_detection = get_recall
    get_true_negative_rate = get_specificity
    get_f_measure = get_f1_score

    def get_false_positive_rate(self) -> float:
        """Calculate false positive rate."""
        if not hasattr(self, 'false_positive'):
            # Calculate for positive class in multi-class
            class_metrics = self.get_class_metrics(class_index=1)
            return 1 - class_metrics['specificity']
            
        denominator = self.false_positive + self.true_negative
        self._validate_non_zero_denominator(denominator, "false positive rate")
        return self.false_positive / denominator

    def get_false_negative_rate(self) -> float:
        """Calculate false negative rate."""
        return 1 - self.get_recall()

    # More aliases
    get_type_1_error = get_false_positive_rate
    get_probability_of_false_alarm = get_false_positive_rate
    get_type_2_error = get_false_negative_rate

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all available metrics."""
        metrics = {
            'accuracy': self.get_accuracy(),
            'error_rate': self.get_error_rate(),
        }
        
        if self.n_classes == 2:
            # Binary metrics
            try:
                metrics.update({
                    'precision': self.get_precision(),
                    'recall': self.get_recall(),
                    'specificity': self.get_specificity(),
                    'f1_score': self.get_f1_score(),
                    'false_positive_rate': self.get_false_positive_rate(),
                    'false_negative_rate': self.get_false_negative_rate(),
                })
                
                if hasattr(self, 'get_g_mean'):
                    metrics['g_mean'] = self.get_g_mean()
                if hasattr(self, 'get_balance'):
                    metrics['balance'] = self.get_balance()
                if hasattr(self, 'get_matthews_correlation_coefficient'):
                    metrics['matthews_correlation_coefficient'] = self.get_matthews_correlation_coefficient()
                    
            except ZeroDivisionError as e:
                metrics['error'] = str(e)
        else:
            # Multi-class metrics
            metrics.update(self.get_macro_metrics())
            metrics.update(self.get_weighted_metrics())
            
            # Per-class metrics
            metrics['per_class_metrics'] = {}
            for i, label in enumerate(self.labels):
                try:
                    metrics['per_class_metrics'][str(label)] = self.get_class_metrics(class_index=i)
                except:
                    pass
        
        return metrics

    # Keep existing binary-specific methods for backward compatibility
    def get_g_mean(self) -> float:
        """Calculate geometric mean (binary only)."""
        if self.n_classes != 2:
            raise ValueError("G-mean is only available for binary classification")
        return math.sqrt(self.get_precision() * self.get_recall())

    def get_balance(self) -> float:
        """Calculate balance metric (binary only)."""
        if self.n_classes != 2:
            raise ValueError("Balance is only available for binary classification")
        fpr = self.get_false_positive_rate()
        tpr = self.get_recall()
        return 1 - (math.sqrt((0 - fpr)**2 + (1 - tpr)**2)) / math.sqrt(2)

    def get_matthews_correlation_coefficient(self) -> float:
        """Calculate Matthews Correlation Coefficient (binary only)."""
        if self.n_classes != 2:
            raise ValueError("MCC is only available for binary classification")
            
        numerator = (self.true_positive * self.true_negative - 
                    self.false_positive * self.false_negative)
        
        denominator = math.sqrt(
            (self.true_positive + self.false_positive) *
            (self.true_positive + self.false_negative) *
            (self.true_negative + self.false_positive) *
            (self.true_negative + self.false_negative)
        )
        
        self._validate_non_zero_denominator(denominator, "Matthews Correlation Coefficient")
        return numerator / denominator

    def false_rate(self) -> float:
        """Calculate false rate (same as error rate)."""
        return self.get_error_rate()

    @classmethod
    def from_predictions(cls, y_true: List[Any], y_pred: List[Any], 
                        labels: Optional[List[Any]] = None) -> 'DConfusion':
        """
        Create DConfusion object from actual and predicted labels.
        
        Args:
            y_true: List of actual labels
            y_pred: List of predicted labels
            labels: List of all possible labels (for multi-class)
            
        Returns:
            DConfusion: New DConfusion object
        """
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have the same length")
        
        # Determine unique labels
        if labels is None:
            unique_labels = sorted(list(set(y_true + y_pred)))
        else:
            unique_labels = list(labels)
        
        n_classes = len(unique_labels)
        
        # Create label to index mapping
        label_to_idx = {label: i for i, label in enumerate(unique_labels)}
        
        # Initialize confusion matrix
        matrix = np.zeros((n_classes, n_classes), dtype=int)
        
        # Fill confusion matrix
        for true_label, pred_label in zip(y_true, y_pred):
            true_idx = label_to_idx[true_label]
            pred_idx = label_to_idx[pred_label]
            matrix[true_idx, pred_idx] += 1
        
        return cls(confusion_matrix=matrix, labels=unique_labels)