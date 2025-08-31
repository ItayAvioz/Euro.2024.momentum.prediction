"""
ARIMAX Model Implementation

ARIMAX models for momentum prediction with exogenous variables:
1. momentum_change → momentum_change (with momentum as exogenous)

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import warnings

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("Warning: ARIMA libraries not available. Install with: pip install statsmodels")

from .base_model import BaseMomentumModel

class ARIMAXModel(BaseMomentumModel):
    """ARIMAX implementation for momentum prediction with exogenous variables."""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        """Initialize ARIMAX model."""
        super().__init__(model_name, config)
        
        if not ARIMA_AVAILABLE:
            raise ImportError("ARIMA libraries not available")
            
        self.arima_config = config.get('arima_params', {})
        self.order = None
        self.fitted_model = None
        self.exog_train = None
        
    def fit(self, train_data: pd.Series, exog_data: Optional[pd.Series] = None) -> None:
        """
        Train ARIMAX model on univariate time series with exogenous variables.
        
        Args:
            train_data: Time series training data (chronologically ordered)
            exog_data: Exogenous variables for training (same length as train_data)
        """
        # Validate data
        is_valid, error_msg = self.validate_data(train_data)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error_msg}")
        
        # Ensure chronological order and clean data
        train_data = train_data.sort_index()
        train_data = train_data.replace([np.inf, -np.inf], np.nan)
        train_data = train_data.dropna()
        
        # Handle exogenous data if provided
        if exog_data is not None:
            exog_data = exog_data.sort_index()
            exog_data = exog_data.replace([np.inf, -np.inf], np.nan)
            exog_data = exog_data.dropna()
            
            # Ensure same length after cleaning
            min_length = min(len(train_data), len(exog_data))
            train_data = train_data.iloc[:min_length]
            exog_data = exog_data.iloc[:min_length]
            
            # Store for prediction
            self.exog_train = exog_data.values.reshape(-1, 1)
        
        if len(train_data) < 5:
            raise ValueError("Insufficient training data after cleaning")
        
        self.training_data_size = len(train_data)
        
        try:
            # Try different ARIMA orders with exogenous variables
            self.fitted_model = None
            for order in [(1, 1, 1), (0, 1, 1), (1, 0, 1), (0, 1, 0)]:
                try:
                    if exog_data is not None:
                        # ARIMAX with exogenous variables
                        self.fitted_model = ARIMA(
                            train_data, 
                            order=order,
                            exog=self.exog_train
                        ).fit()
                    else:
                        # Regular ARIMA
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
            model_type = "ARIMAX" if exog_data is not None else "ARIMA"
            print(f"{model_type}{self.order} fitted successfully on {len(train_data)} observations")
            
        except Exception as e:
            # Fallback to simple mean prediction
            print(f"ARIMAX fitting failed: {e}. Using mean prediction fallback.")
            self.fitted_model = train_data.mean()
            self.order = (0, 0, 0)
            self.is_fitted = True
    
    def predict(self, steps: int, exog_future: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Generate ARIMAX predictions.
        
        Args:
            steps: Number of future time steps to predict
            exog_future: Exogenous variables for prediction period (steps x n_features)
            
        Returns:
            Array of predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            if hasattr(self.fitted_model, 'forecast'):
                # Statsmodels ARIMA/ARIMAX model
                if exog_future is not None:
                    # ARIMAX prediction with exogenous variables
                    forecast = self.fitted_model.forecast(steps=steps, exog=exog_future)
                else:
                    # Regular ARIMA prediction
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
            'model_type': 'ARIMAX' if self.exog_train is not None else 'ARIMA',
            'has_exog': self.exog_train is not None
        }

class MomentumARIMAXPredictor:
    """Manages multiple ARIMAX models for momentum prediction."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize predictor with configuration."""
        self.config = config
        self.models = {}
        
    def create_model(self, model_type: str) -> ARIMAXModel:
        """
        Create ARIMAX model for specific prediction type.
        
        Args:
            model_type: Model configuration name
            
        Returns:
            Configured ARIMAX model
        """
        return ARIMAXModel(model_type, self.config)
    
    def train_models(self, momentum_series: pd.Series, change_series: pd.Series) -> Dict[str, ARIMAXModel]:
        """
        Train momentum prediction models (both ARIMA and ARIMAX).
        
        Args:
            momentum_series: Momentum time series data
            change_series: Momentum change time series data
            
        Returns:
            Dictionary of trained models
        """
        models = {}
        
        # Train momentum → momentum model (ARIMA)
        try:
            momentum_model = self.create_model('momentum_to_momentum')
            momentum_model.fit(momentum_series)
            models['momentum'] = momentum_model
            print("✅ Momentum ARIMA model trained successfully")
        except Exception as e:
            print(f"❌ Failed to train momentum model: {e}")
            
        # Train change → change model (ARIMA)
        try:
            change_model = self.create_model('change_to_change')
            change_model.fit(change_series)
            models['change'] = change_model
            print("✅ Change ARIMA model trained successfully")
        except Exception as e:
            print(f"❌ Failed to train change model: {e}")
        
        # Train change → change model with momentum as exogenous (ARIMAX)
        try:
            arimax_model = self.create_model('momentum_to_change_arimax')
            arimax_model.fit(change_series, momentum_series)
            models['arimax'] = arimax_model
            print("✅ Momentum→Change ARIMAX model trained successfully")
        except Exception as e:
            print(f"❌ Failed to train ARIMAX model: {e}")
        
        self.models = models
        return models
    
    def predict_all(self, steps: int, momentum_future: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Generate predictions from all trained models.
        
        Args:
            steps: Number of time steps to predict
            momentum_future: Future momentum values for ARIMAX prediction
            
        Returns:
            Dictionary of predictions by model type
        """
        predictions = {}
        
        for model_type, model in self.models.items():
            try:
                if model_type == 'arimax' and momentum_future is not None:
                    # ARIMAX prediction with exogenous variables
                    pred = model.predict(steps, momentum_future.reshape(-1, 1))
                else:
                    # Regular ARIMA prediction
                    pred = model.predict(steps)
                
                predictions[model_type] = pred
                print(f"✅ Generated {len(pred)} predictions for {model_type}")
            except Exception as e:
                print(f"❌ Prediction failed for {model_type}: {e}")
                predictions[model_type] = np.full(steps, np.nan)
        
        return predictions
