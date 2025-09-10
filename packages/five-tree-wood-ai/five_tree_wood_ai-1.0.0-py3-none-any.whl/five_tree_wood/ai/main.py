#!/usr/bin/env python3
"""
Aircon AI Training Script and REST API
"""

import argparse
import sys
import os
from datetime import datetime

from flask import Flask, jsonify, request

from five_tree_wood.ai.aircon import (
    predict_temperature,
    train_model,
    verify_model_loaded,
)
from five_tree_wood.ai.conf import set_config_dir

# Flask app for REST API
app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict_api():
    """
    REST API endpoint for temperature prediction.

    Expected JSON payload:
    {
        "time": "2025-09-08T14:30:00" or "now" for current time,
        "inside_temperature": 22.5,
        "outside_temperature": 15.0,
        "roof_temperature": 18.0
    }

    Returns:
    {
        "prediction": 23.1,
        "status": "success"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided", "status": "error"}), 400

        # Extract parameters
        time_str = data.get("time")
        inside_temp = data.get("inside_temperature")
        outside_temp = data.get("outside_temperature")
        roof_temp = data.get("roof_temperature")
        carine_temp_max_0 = data.get("carine_temp_max_0")
        carine_temp_min_1 = data.get("carine_temp_min_1")

        # Validate required parameters
        if any(
            param is None
            for param in [
                time_str,
                inside_temp,
                outside_temp,
                roof_temp,
                carine_temp_max_0,
                carine_temp_min_1,
            ]
        ):
            return (
                jsonify(
                    {
                        "error": "Missing required parameters: "
                        "time, inside_temperature, outside_temperature, "
                        "roof_temperature, carine_temp_max_0, carine_temp_min_1",
                        "status": "error",
                    }
                ),
                400,
            )

        # Handle time parameter
        if time_str == "now":
            time_value = datetime.now()
        else:
            time_value = time_str

        # Make prediction
        prediction = predict_temperature(
            time=time_value,
            inside_temperature=float(inside_temp),
            outside_temperature=float(outside_temp),
            roof_temperature=float(roof_temp),
            carine_temp_max_0=float(carine_temp_max_0),
            carine_temp_min_1=float(carine_temp_min_1),
        )

        return jsonify(
            {
                "prediction": float(prediction),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except ValueError as e:
        return (
            jsonify(
                {"error": f"Invalid parameter values: {str(e)}", "status": "error"}
            ),
            400,
        )
    except Exception as e:  # pylint: disable=broad-except
        # Catch-all for unexpected errors to avoid leaking stack traces in API
        return (
            jsonify({"error": f"Prediction failed: {str(e)}", "status": "error"}),
            500,
        )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        # Try to load the model to verify it's available
        verify_model_loaded()
        return jsonify(
            {
                "status": "healthy",
                "model_loaded": True,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except (ImportError, RuntimeError) as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "model_loaded": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/info", methods=["GET"])
def info():
    """API information endpoint."""
    return jsonify(
        {
            "name": "Aircon AI Prediction API",
            "version": "1.0.0",
            "description": "Predicts inside temperature one hour in the future",
            "endpoints": {
                "/predict": "POST - Make temperature prediction",
                "/health": "GET - Health check",
                "/info": "GET - API information",
                "/train": "POST - Train the model",
            },
            "example_request": {
                "time": "2025-09-08T14:30:00",
                "inside_temperature": 22.5,
                "outside_temperature": 15.0,
                "roof_temperature": 18.0,
                "carine_temp_max_0": 25.0,
                "carine_temp_min_1": 12.0,
            },
        }
    )


@app.route("/train", methods=["POST"])
def train_api():
    """Train the model via API."""
    try:
        print("Starting model training via API...")
        _, feature_names = train_model()
        return jsonify(
            {
                "status": "success",
                "message": "Model trained successfully",
                "features": feature_names,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:  # pylint: disable=broad-except
        # Catch-all for unexpected errors to avoid leaking stack traces in API
        return (
            jsonify(
                {
                    "status": "error",
                    "error": f"Training failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


def train_main():
    """Train the model from command line."""
    print("Starting Aircon AI model training...")
    _, feature_names = train_model()
    print("Training completed successfully!")
    print(f"Model trained with features: {feature_names}")


def run_api(host="0.0.0.0", port=5000, debug=False):
    """Run the Flask API server."""
    print(f"Starting Aircon AI Prediction API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


def predict_main():
    """Make a prediction from command line."""

    if len(sys.argv) < 8:
        print(
            "Usage: python main.py predict <time> <inside_temp> "
            "<outside_temp> <roof_temp> <carine_temp_max_0> <carine_temp_min_1>"
        )
        print("  time               - ISO datetime string or 'now'")
        print("  inside_temp        - Current inside temperature")
        print("  outside_temp       - Current outside temperature")
        print("  roof_temp          - Current roof temperature")
        print("  carine_temp_max_0  - Carine max temp sensor")
        print("  carine_temp_min_1  - Carine min temp sensor")
        print("Example: python main.py predict now 22.5 15.0 18.0 25.0 12.0")
        return

    try:
        time_str = sys.argv[2]
        inside_temp = float(sys.argv[3])
        outside_temp = float(sys.argv[4])
        roof_temp = float(sys.argv[5])
        carine_temp_max_0 = float(sys.argv[6])
        carine_temp_min_1 = float(sys.argv[7])

        # Handle time parameter
        if time_str == "now":
            time_value = datetime.now()
        else:
            time_value = time_str

        print("Making prediction with:")
        print(f"  Time: {time_value}")
        print(f"  Inside temperature: {inside_temp}°C")
        print(f"  Outside temperature: {outside_temp}°C")
        print(f"  Roof temperature: {roof_temp}°C")
        print(f"  Carine temp max 0: {carine_temp_max_0}°C")
        print(f"  Carine temp min 1: {carine_temp_min_1}°C")

        # Make prediction
        prediction = predict_temperature(
            time=time_value,
            inside_temperature=inside_temp,
            outside_temperature=outside_temp,
            roof_temperature=roof_temp,
            carine_temp_max_0=carine_temp_max_0,
            carine_temp_min_1=carine_temp_min_1,
        )

        print(f"Predicted inside temperature in 1 hour: {prediction:.2f}°C")

    except ValueError as e:
        print(f"Error: Invalid parameter values - {e}")
    except Exception as e:  # pylint: disable=broad-except
        # Catch-all for unexpected errors in CLI
        print(f"Error: Prediction failed - {e}")


def main():
    """
    Main function - can train model, run API, or make predictions based on arguments.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Aircon AI - Temperature Prediction System"
    )
    parser.add_argument(
        "-C",
        "--conf-dir",
        default=None,
        help="Configuration directory (default: ./conf)",
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # API command
    api_parser = subparsers.add_parser("api", help="Run the REST API server")
    api_parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=5000, help="Port to bind to")

    # Train command
    _ = subparsers.add_parser("train", help="Train the model")

    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", help="Make a temperature prediction"
    )
    predict_parser.add_argument("time", help='ISO datetime string or "now"')
    predict_parser.add_argument(
        "inside_temp", type=float, help="Current inside temperature"
    )
    predict_parser.add_argument(
        "outside_temp", type=float, help="Current outside temperature"
    )
    predict_parser.add_argument(
        "roof_temp", type=float, help="Current roof temperature"
    )
    predict_parser.add_argument(
        "carine_temp_max_0", type=float, help="Carine max temp sensor"
    )
    predict_parser.add_argument(
        "carine_temp_min_1", type=float, help="Carine min temp sensor"
    )

    args = parser.parse_args()

    # Set configuration directory from environment variable first, then command line
    config_dir = os.environ.get('FIVTREEWD_CONFIG_DIR') or args.conf_dir
    if config_dir:
        set_config_dir(config_dir)

    # Execute commands
    if args.command == "api":
        run_api(host=args.host, port=args.port, debug=args.debug)
    elif args.command == "train":
        train_main()
    elif args.command == "predict":
        predict_main_new(args)
    else:
        # Default behavior - run the API
        run_api()


def predict_main_new(args):
    """Make a prediction using parsed arguments."""
    try:
        # Handle time parameter
        if args.time == "now":
            time_value = datetime.now()
        else:
            time_value = args.time

        print("Making prediction with:")
        print(f"  Time: {time_value}")
        print(f"  Inside temperature: {args.inside_temp}°C")
        print(f"  Outside temperature: {args.outside_temp}°C")
        print(f"  Roof temperature: {args.roof_temp}°C")
        print(f"  Carine temp max 0: {args.carine_temp_max_0}°C")
        print(f"  Carine temp min 1: {args.carine_temp_min_1}°C")

        # Make prediction
        prediction = predict_temperature(
            time=time_value,
            inside_temperature=args.inside_temp,
            outside_temperature=args.outside_temp,
            roof_temperature=args.roof_temp,
            carine_temp_max_0=args.carine_temp_max_0,
            carine_temp_min_1=args.carine_temp_min_1,
        )

        print(f"Predicted inside temperature in 1 hour: {prediction:.2f}°C")

    except ValueError as e:
        print(f"Error: Invalid parameter values - {e}")
    except Exception as e:  # pylint: disable=broad-except
        # Catch-all for unexpected errors in CLI
        print(f"Error: Prediction failed - {e}")


if __name__ == "__main__":
    main()
