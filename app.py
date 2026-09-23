"""
Flask Web Application for Taiwan Weather Forecast (Vercel Deployment)
Integrates with CWA Open Data API, SQLite Database (data.db), and renders interactive weather dashboard.
"""

import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify, request
from fetch_data import run_etl_pipeline
from database import query_all_forecasts, query_distinct_regions, query_forecast_by_region, DEFAULT_DB_PATH

app = Flask(__name__)


def ensure_db_ready():
    """Ensure database exists and contains weather data before servicing requests."""
    try:
        df = query_all_forecasts()
        if df.empty:
            print("[Flask] DB is empty, triggering initial CWA ETL fetch...")
            run_etl_pipeline()
    except Exception as e:
        print(f"[Flask] Error checking DB, running ETL pipeline: {e}")
        try:
            run_etl_pipeline()
        except Exception as err:
            print(f"[Flask] ETL execution failed: {err}")


@app.route("/")
def index():
    """Render main Taiwan Weather Forecast Dashboard page."""
    ensure_db_ready()
    regions = query_distinct_regions()
    if not regions:
        regions = ["北部地區", "中部地區", "南部地區", "東北部地區", "東部地區", "東南部地區", "離島地區"]
    
    selected_region = request.args.get("region", regions[0] if regions else "北部地區")
    region_data = query_forecast_by_region(selected_region)
    all_data = query_all_forecasts()

    # Convert DataFrames to dict lists for JSON / Jinja template
    region_records = region_data.to_dict(orient="records") if not region_data.empty else []
    all_records = all_data.to_dict(orient="records") if not all_data.empty else []

    return render_template(
        "index.html",
        regions=regions,
        selected_region=selected_region,
        region_records=region_records,
        all_records=all_records
    )


@app.route("/api/weather")
def api_weather():
    """REST API endpoint for weather forecast data."""
    ensure_db_ready()
    region = request.args.get("region")
    if region:
        df = query_forecast_by_region(region)
    else:
        df = query_all_forecasts()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/sync", methods=["POST", "GET"])
def api_sync():
    """API endpoint to trigger live CWA API ETL sync."""
    try:
        count = run_etl_pipeline()
        return jsonify({"status": "success", "count": count, "message": "ETL sync completed successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    ensure_db_ready()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
