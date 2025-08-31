"""
Base Model Abstract Class for ARIMA Models

Defines the interface for momentum prediction models.

Author: AI Assistant  
Date: August 2024
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any

class BaseMomentumModel(ABC):
    """Abstract base class for momentum prediction models."""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """
        Initialize the base model.
        
        Args:
            model_name: Name/type of model
            config: Configuration dictionary
        """
        self.model_name = model_name
        self.config = config
        self.is_fitted = False
        self.model = None
        self.training_data_size = 0
        
    @abstractmethod
    def fit(self, train_data: pd.Series) -> None:
        """
        Train the model on training data.
        
        Args:
            train_data: Time series data for training (chronologically ordered)
        """
        pass
    
    @abstractmethod
    def predict(self, steps: int) -> np.ndarray:
        """
        Generate predictions for future time steps.
        
        Args:
            steps: Number of future steps to predict
            
        Returns:
            Array of predictions
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and parameters.
        
        Returns:
            Dictionary with model details
        """
        pass
    
    def validate_data(self, data: pd.Series) -> Tuple[bool, str]:
        """
        Validate input data quality.
        
        Args:
            data: Time series data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        min_obs = self.config.get('validation', {}).get('min_train_observations', 10)
        max_missing = self.config.get('validation', {}).get('max_missing_ratio', 0.2)
        
        if len(data) < min_obs:
            return False, f"Insufficient data: {len(data)} < {min_obs}"
            
        if data.isnull().sum() / len(data) > max_missing:
            return False, f"Too many missing values: {data.isnull().sum()}/{len(data)}"
            
        if data.isnull().all():
            return False, "All values are missing"
            
        return True, "Data is valid"
    
    def calculate_adjusted_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Adjusted R² for fit quality."""
        from sklearn.metrics import r2_score
        
        # Ensure numeric types
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)
        
        if len(y_true) <= 1:
            return float('-inf')
            
        r2 = r2_score(y_true, y_pred)
        n = len(y_true)
        p = 1  # Number of features
        
        adjusted_r2 = 1 - ((1 - r2) * (n - 1) / (n - p - 1))
        return adjusted_r2
    
    def calculate_directional_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Directional Accuracy for trend prediction."""
        # Ensure numeric types
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)
        
        if len(y_true) < 2:
            return 0.0
            
        actual_directions = np.diff(y_true) > 0
        predicted_directions = np.diff(y_pred) > 0
        
        correct_directions = actual_directions == predicted_directions
        return np.mean(correct_directions)
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Comprehensive model evaluation.
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            Dictionary of evaluation metrics
        """
        from sklearn.metrics import mean_squared_error
        
        # Convert to numpy arrays and ensure numeric types
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)
        
        # Ensure same length
        min_length = min(len(y_true), len(y_pred))
        y_true = y_true[:min_length]
        y_pred = y_pred[:min_length]
        
        # Remove infinite values
        mask = np.isfinite(y_true) & np.isfinite(y_pred)
        y_true_clean = y_true[mask]
        y_pred_clean = y_pred[mask]
        
        if len(y_true_clean) == 0:
            return {
                'mse': float('inf'),
                'adjusted_r2': float('-inf'),
                'directional_accuracy': 0.0,
                'n_predictions': 0
            }
        
        try:
            mse = mean_squared_error(y_true_clean, y_pred_clean)
            adjusted_r2 = self.calculate_adjusted_r2(y_true_clean, y_pred_clean)
            directional_accuracy = self.calculate_directional_accuracy(y_true_clean, y_pred_clean)
            
            return {
                'mse': mse,
                'adjusted_r2': adjusted_r2,
                'directional_accuracy': directional_accuracy,
                'n_predictions': len(y_true_clean)
            }
            
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return {
                'mse': float('inf'),
                'adjusted_r2': float('-inf'),
                'directional_accuracy': 0.0,
                'n_predictions': 0
            }
