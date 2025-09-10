"""
Prediction utilities for Five Tree Wood AI.
"""

import logging
import os

import joblib
import numpy as np
import pandas as pd

from ..conf import get_config_dir

logger = logging.getLogger(__name__)


def _load_model():
    """Load the trained model from disk and cache it as a function attribute."""
    if not hasattr(_load_model, "cached_model"):
        # Get the path to the saved model
        conf_dir = get_config_dir()
        model_path = os.path.join(conf_dir, "aircon_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. "
                "Please train the model first."
            )
        _load_model.cached_model = joblib.load(model_path)
        logger.debug("Model loaded from %s", model_path)
    return _load_model.cached_model


def verify_model_loaded():
    """Verify if the model is loaded."""
    try:
        _load_model()
        return True
    except (
        FileNotFoundError,
        joblib.externals.loky.process_executor.TerminatedWorkerError,
        joblib.externals.loky.process_executor.BrokenProcessPool,
    ) as e:
        logger.debug("Model loading failed: %s", e)
        return False


def predict_temperature(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    time,
    inside_temperature,
    outside_temperature,
    roof_temperature,
    carine_temp_max_0,
    carine_temp_min_1,
):
    """
    Predict the inside temperature one hour in the future.

    Args:
        time: datetime object or string representing the current time
        inside_temperature: float, current inside temperature
        outside_temperature: float, current outside temperature
        roof_temperature: float, current roof temperature
        carine_temp_max_0: float, carine max temp sensor
        carine_temp_min_1: float, carine min temp sensor

    Returns:
        float: predicted inside temperature one hour in the future
    """
    # Load the cached model
    model = _load_model()

    # Convert time to datetime if it's a string
    if isinstance(time, str):
        time = pd.to_datetime(time)
    elif not isinstance(time, pd.Timestamp):
        time = pd.Timestamp(time)

    # Calculate time features
    seconds_since_midnight = time.hour * 3600 + time.minute * 60 + time.second

    seconds_in_day = 24 * 60 * 60
    time_sin = np.sin(2 * np.pi * seconds_since_midnight / seconds_in_day)
    time_cos = np.cos(2 * np.pi * seconds_since_midnight / seconds_in_day)

    # Calculate seasonal features (Southern Hemisphere)
    summer_solstice = pd.to_datetime(f"{time.year}-12-21", utc=True)
    if time.tz is None:
        time = time.tz_localize("UTC")

    days_since_solstice = (time - summer_solstice).days % 365
    solstice_sin = np.sin(2 * np.pi * days_since_solstice / 365)
    solstice_cos = np.cos(2 * np.pi * days_since_solstice / 365)

    # Create feature DataFrame with explicit column names
    feature_names = [
        "inside_temperature",
        "time_sin",
        "time_cos",
        "solstice_sin",
        "solstice_cos",
        "outside_temperature",
        "roof_temperature",
        "carine_temp_max_0",
        "carine_temp_min_1",
    ]
    feature_values = [
        [
            inside_temperature,
            time_sin,
            time_cos,
            solstice_sin,
            solstice_cos,
            outside_temperature,
            roof_temperature,
            carine_temp_max_0,
            carine_temp_min_1,
        ]
    ]
    features = pd.DataFrame(feature_values, columns=feature_names)

    # Make prediction
    prediction = model.predict(features)[0]

    return prediction
