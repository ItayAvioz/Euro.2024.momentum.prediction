"""
ARIMA Model Implementation

Pure ARIMA models for momentum prediction:
1. momentum → momentum
2. momentum_change → momentum_change

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import warnings

try:
    from statsmodels.tsa.arima.model import ARIMA
    # Try importing pmdarima (auto_arima)
    try:
        from pmdarima import auto_arima
        AUTO_ARIMA_AVAILABLE = True
    except ImportError:
        AUTO_ARIMA_AVAILABLE = False
        print("Warning: pmdarima not available. Using manual ARIMA parameters.")
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    AUTO_ARIMA_AVAILABLE = False
    print("Warning: ARIMA libraries not available. Install with: pip install statsmodels")

from .base_model import BaseMomentumModel

class PureARIMAModel(BaseMomentumModel):
    """Pure ARIMA implementation for univariate momentum prediction."""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """Initialize ARIMA model."""
        super().__init__(model_name, config)
        
        if not ARIMA_AVAILABLE:
            raise ImportError("ARIMA libraries not available")
            
        self.arima_config = config.get('arima_params', {})
        self.order = None
        self.fitted_model = None
        
    def fit(self, train_data: pd.Series) -> None:
        """
        Train ARIMA model on univariate time series.
        
        Args:
            train_data: Time series training data (chronologically ordered)
        """
        # Validate data
        is_valid, error_msg = self.validate_data(train_data)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error_msg}")
        
        # Ensure chronological order and clean data
        train_data = train_data.sort_index()
        train_data = train_data.replace([np.inf, -np.inf], np.nan)
        train_data = train_data.dropna()
        
        if len(train_data) < 5:
            raise ValueError("Insufficient training data after cleaning")
        
        self.training_data_size = len(train_data)
        
        try:
            # Use statsmodels ARIMA directly for simplicity
            # Try different simple orders
            self.fitted_model = None
            for order in [(1, 1, 1), (0, 1, 1), (1, 0, 1), (0, 1, 0)]:
                try:
                    self.fitted_model = ARIMA(train_data, order=order).fit()
                    self.order = order
                    break
                except Exception as e:
                    print(f"Failed to fit ARIMA{order}: {e}")
                    continue
            
            # If all failed, use mean fallback
            if self.fitted_model is None:
                print("All ARIMA orders failed, using mean fallback")
                self.fitted_model = train_data.mean()
                self.order = (0, 0, 0)
            
            self.is_fitted = True
            print(f"ARIMA{self.order} fitted successfully on {len(train_data)} observations")
            
        except Exception as e:
            # Fallback to simple mean prediction
            print(f"ARIMA fitting failed: {e}. Using mean prediction fallback.")
            self.fitted_model = train_data.mean()
            self.order = (0, 0, 0)  # No ARIMA, just mean
            self.is_fitted = True
    
    def predict(self, steps: int) -> np.ndarray:
        """
        Generate ARIMA predictions.
        
        Args:
            steps: Number of future time steps to predict
            
        Returns:
            Array of predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            if hasattr(self.fitted_model, 'forecast'):
                # Statsmodels ARIMA model
                forecast = self.fitted_model.forecast(steps=steps)
                
                # Handle pandas Series or numpy array
                if hasattr(forecast, 'values'):
                    result = np.array(forecast.values, dtype=float)
                else:
                    result = np.array(forecast, dtype=float)
                
                return result
            else:
                # Fallback mean prediction (fitted_model is a scalar in this case)
                return np.full(steps, float(self.fitted_model))
                
        except Exception as e:
            print(f"Prediction failed: {e}. Using fallback.")
            return np.full(steps, 0.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and parameters."""
        return {
            'model_name': self.model_name,
            'arima_order': self.order,
            'training_size': self.training_data_size,
            'is_fitted': self.is_fitted,
            'model_type': 'Pure ARIMA'
        }

class MomentumARIMAPredictor:
    """Manages multiple ARIMA models for momentum prediction."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize predictor with configuration."""
        self.config = config
        self.models = {}
        
    def create_model(self, model_type: str) -> PureARIMAModel:
        """
        Create ARIMA model for specific prediction type.
        
        Args:
            model_type: 'momentum_to_momentum' or 'change_to_change'
            
        Returns:
            Configured ARIMA model
        """
        return PureARIMAModel(model_type, self.config)
    
    def train_models(self, momentum_series: pd.Series, change_series: pd.Series) -> Dict[str, PureARIMAModel]:
        """
        Train both momentum and change ARIMA models.
        
        Args:
            momentum_series: Momentum time series data
            change_series: Momentum change time series data
            
        Returns:
            Dictionary of trained models
        """
        models = {}
        
        # Train momentum → momentum model
        try:
            momentum_model = self.create_model('momentum_to_momentum')
            momentum_model.fit(momentum_series)
            models['momentum'] = momentum_model
            print("✅ Momentum ARIMA model trained successfully")
        except Exception as e:
            print(f"❌ Failed to train momentum model: {e}")
            
        # Train change → change model  
        try:
            change_model = self.create_model('change_to_change')
            change_model.fit(change_series)
            models['change'] = change_model
            print("✅ Change ARIMA model trained successfully")
        except Exception as e:
            print(f"❌ Failed to train change model: {e}")
        
        self.models = models
        return models
    
    def predict_all(self, steps: int) -> Dict[str, np.ndarray]:
        """
        Generate predictions from all trained models.
        
        Args:
            steps: Number of time steps to predict
            
        Returns:
            Dictionary of predictions by model type
        """
        predictions = {}
        
        for model_type, model in self.models.items():
            try:
                pred = model.predict(steps)
                predictions[model_type] = pred
                print(f"✅ Generated {len(pred)} predictions for {model_type}")
            except Exception as e:
                print(f"❌ Prediction failed for {model_type}: {e}")
                predictions[model_type] = np.full(steps, np.nan)
        
        return predictions
