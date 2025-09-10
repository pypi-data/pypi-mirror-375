"""
Five Tree Wood AI model training utilities.
"""

import logging
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ..conf import get_config, get_config_dir

logger = logging.getLogger(__name__)


def train_model():
    """Train the aircon AI model using InfluxDB data."""
    df = _fetch_data()

    logger.debug("Training model...")

    # Define features and target

    x_features = df[
        [
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
    ]
    y_target = df["inside_temperature_1h"]

    # Train model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(x_features, y_target)

    # Get configuration directory
    conf_dir = get_config_dir()

    # Get feature importances
    importances = model.feature_importances_
    features = x_features.columns
    for name, score in zip(features, importances):
        logger.debug("%s: %.4f", name, score)

    # Make predictions and calculate metrics
    y_pred = model.predict(x_features)
    mae = mean_absolute_error(y_target, y_pred)
    mse = mean_squared_error(y_target, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_target, y_pred)
    logger.debug("Mean Absolute Error (MAE): %s", mae)
    logger.debug("Mean Squared Error (MSE): %s", mse)
    logger.debug("Root Mean Squared Error (RMSE): %s", rmse)
    logger.debug("R² Score: %s", r2)

    # Write training information to log file
    log_path = os.path.join(conf_dir, "training.log")

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n{'='*60}\n")
        log_file.write(f"Training Run: {datetime.now().isoformat()}\n")
        log_file.write(f"{'='*60}\n")
        log_file.write(f"Dataset Size: {len(df)} samples\n")
        log_file.write("Model: RandomForestRegressor (n_estimators=10)\n\n")

        log_file.write("Performance Metrics:\n")
        log_file.write(f"  Mean Absolute Error (MAE): {mae:.4f}\n")
        log_file.write(f"  Mean Squared Error (MSE): {mse:.4f}\n")
        log_file.write(f"  Root Mean Squared Error (RMSE): {rmse:.4f}\n")
        log_file.write(f"  R² Score: {r2:.4f}\n\n")

        log_file.write("Feature Importances:\n")
        for name, score in zip(features, importances):
            log_file.write(f"  {name}: {score:.4f}\n")
        log_file.write("\n")

    logger.debug("Training log written to %s", log_path)

    # Save the trained model
    # Create conf directory and set up file paths
    os.makedirs(conf_dir, exist_ok=True)
    model_path = os.path.join(conf_dir, "aircon_model.pkl")

    joblib.dump(model, model_path)
    logger.debug("Model saved as %s", model_path)

    return model, x_features.columns.tolist()


def _fetch_data(start="-3y"):
    """Fetch data from InfluxDB for training."""

    # Load configuration from both config.ini and secrets.ini
    config = get_config()
    influx_config = config["influxdb"]

    url = influx_config["url"]
    token = influx_config["token"]
    org = influx_config["org"]
    bucket = influx_config.get("bucket", "homeassistant")

    print("Loading data...")

    # Connect to InfluxDB and query data
    with InfluxDBClient(url=url, token=token, org=org, timeout="5m") as client:
        query_api = client.query_api()

        # Flux query to get the required data with future inside temperature
        query = f"""
    mainData = from(bucket: "{bucket}")
        |> range(start: {start})
        |> filter(fn: (r) =>
        ((r["entity_id"] == "inside_temperature" or
        r["entity_id"] == "outside_temperature" or
        r["entity_id"] == "roof_temperature" or
        r["entity_id"] == "carine_temp_max_0" or
        r["entity_id"] == "carine_temp_min_1"
        ) and r["_field"] == "value" ) or
        (r["entity_id"] == "controller" and r["_field"] == "state")
        )
        |> filter(fn: (r) => r["_field"] == "state" or r["_field"] == "value")
        |> map(fn: (r) => ({{r with _value:
            if r["entity_id"] == "controller" then
                if r["_value"] == "off" then 0.0 else 1.0
            else float(v: r["_value"])
        }}))
        |> aggregateWindow(every: 15m, fn: mean, createEmpty: true)
        |> drop(columns: ["_field", "_start", "_stop", "_measurement", "domain"])
        |> fill(column: "_value", usePrevious: true)
        |> pivot(rowKey:["_time"], columnKey: ["entity_id"], valueColumn: "_value")
        |> filter(fn: (r) => r["controller"] == 0)
        |> drop(columns: ["controller"])
    // Get future inside temperature (1 hour ahead)
    futureTemp = mainData
        |> keep(columns: ["_time", "inside_temperature"])
        |> timeShift(duration: -1h)
        |> rename(columns: {{inside_temperature: "inside_temperature_1h"}})
    // Join current data with future temperature
    join(tables: {{main: mainData, future: futureTemp}}, on: ["_time"])
        |> rename(columns: {{ "_time": "time"}})
        """

        # Execute query and convert to DataFrame
        result = query_api.query_data_frame(query=query)

        # Convert to pandas DataFrame and clean up
        if isinstance(result, list):
            df = pd.concat(result, ignore_index=True)
        else:
            df = result

    logger.debug("Formatting data...")

    # Ensure time is datetime
    df["time"] = pd.to_datetime(df["time"])

    # Convert to time features
    df["seconds_since_midnight"] = (
        df["time"].dt.hour * 3600 + df["time"].dt.minute * 60 + df["time"].dt.second
    )

    seconds_in_day = 24 * 60 * 60

    df["time_sin"] = np.sin(2 * np.pi * df["seconds_since_midnight"] / seconds_in_day)
    df["time_cos"] = np.cos(2 * np.pi * df["seconds_since_midnight"] / seconds_in_day)

    # Summer solstice for each year (Southern Hemisphere)
    # Handle timezone compatibility
    df["summer_solstice"] = df["time"].dt.year.apply(
        lambda x: pd.to_datetime(f"{int(x)}-12-21", utc=True)
    )

    # Wrap negative values to 0–365
    df["days_since_solstice"] = (df["time"] - df["summer_solstice"]).dt.days
    df["days_since_solstice"] = df["days_since_solstice"] % 365

    df["solstice_sin"] = np.sin(2 * np.pi * df["days_since_solstice"] / 365)
    df["solstice_cos"] = np.cos(2 * np.pi * df["days_since_solstice"] / 365)

    return df
