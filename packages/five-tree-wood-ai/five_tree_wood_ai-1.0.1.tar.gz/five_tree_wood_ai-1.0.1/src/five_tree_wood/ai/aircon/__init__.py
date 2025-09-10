"""
Five Tree Wood AI module for temperature prediction
"""

from .predict import predict_temperature, verify_model_loaded
from .train import train_model

# Export main functions at package level
__all__ = ["train_model", "predict_temperature", "verify_model_loaded"]
