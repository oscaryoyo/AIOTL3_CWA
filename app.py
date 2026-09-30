"""
Flask Web Application for Taiwan Weather Forecast (Vercel Deployment)
Integrates with CWA Open Data API, SQLite Database, and renders interactive weather dashboard.
Vercel compatible: uses /tmp for writable SQLite storage.
"""

import os
import shutil

# ── Vercel Compatibility ───────────────────────────────────────────────────────
# Must set DB_PATH env var BEFORE importing database.py so get_db_path() resolves
# to /tmp (the only writable directory on Vercel's read-only filesystem).
_IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_ENV") is not None
if _IS_VERCEL:
    if not os.environ.get("DB_PATH"):
        os.environ["DB_PATH"] = "/tmp/data.db"
    for fname in ["data.db", "typhoon_cache.json", "stations_cache.json", "update_time.txt"]:
        src = os.path.join(os.path.dirname(__file__), fname)
        dst = os.path.join("/tmp", fname)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass

import json
import pandas as pd
from flask import Flask, render_template, jsonify, request
from fetch_data import run_etl_pipeline
from database import (
    query_all_forecasts,
    query_distinct_regions,
    query_distinct_cities,
    query_forecast_by_region,
    query_forecast_by_city,
)
import traceback
import logging

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


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {traceback.format_exc()}")
    return f"<h3>Application Error</h3><pre>{traceback.format_exc()}</pre>", 500


def clean_records(df):
    """Clean and fill default values for rich weather metrics."""
    if df.empty:
        return []
    df = df.copy()
    if "wx" in df.columns:
        df["wx"] = df["wx"].fillna("多雲")
    if "pop" in df.columns:
        df["pop"] = df["pop"].fillna("20")
    if "ci" in df.columns:
        df["ci"] = df["ci"].fillna("舒適")
    if "windSpeed" in df.columns:
        df["windSpeed"] = df["windSpeed"].fillna(2.2)
    if "windDirection" in df.columns:
        df["windDirection"] = df["windDirection"].fillna(45.0)
    if "humidity" in df.columns:
        df["humidity"] = df["humidity"].fillna(72.0)
    if "precipitation" in df.columns:
        df["precipitation"] = df["precipitation"].fillna(0.0)
    return df.to_dict(orient="records")


def load_cached_json(filename, default=None):
    """Load cached JSON data with fallback."""
    if default is None:
        default = []
    for base in [os.path.dirname(__file__), "/tmp"]:
        target = os.path.join(base, filename)
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return default


def get_update_timestamp():
    """Retrieve last updated timestamp."""
    for base in [os.path.dirname(__file__), "/tmp"]:
        target = os.path.join(base, "update_time.txt")
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val:
                        return val
            except Exception:
                pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    """Render main Taiwan Weather Forecast Dashboard page with all cities and regions."""
    ensure_db_ready()
    regions = query_distinct_regions()
    cities = query_distinct_cities()

    selected_city = request.args.get("city")
    selected_region = request.args.get("region")

    if selected_city and selected_city in cities:
        active_location = selected_city
        active_data = query_forecast_by_city(selected_city)
    elif selected_region and selected_region in regions:
        active_location = selected_region
        active_data = query_forecast_by_region(selected_region)
    else:
        active_location = "臺北市" if "臺北市" in cities else (cities[0] if cities else "北部地區")
        active_data = query_forecast_by_city(active_location) if active_location in cities else query_forecast_by_region(active_location)

    all_data = query_all_forecasts()

    location_records = clean_records(active_data)
    all_records = clean_records(all_data)

    typhoons = load_cached_json("typhoon_cache.json")
    stations = load_cached_json("stations_cache.json")
    update_time = get_update_timestamp()

    return render_template(
        "index.html",
        regions=regions,
        cities=cities,
        selected_location=active_location,
        location_records=location_records,
        all_records=all_records,
        typhoons=typhoons,
        stations=stations,
        update_time=update_time
    )


@app.route("/api/weather")
def api_weather():
    """REST API endpoint for weather forecast data."""
    ensure_db_ready()
    city = request.args.get("city")
    region = request.args.get("region")
    if city:
        df = query_forecast_by_city(city)
    elif region:
        df = query_forecast_by_region(region)
    else:
        df = query_all_forecasts()
    return jsonify(clean_records(df))


@app.route("/api/typhoon")
def api_typhoon():
    """REST API endpoint for typhoon track and forecast data."""
    return jsonify(load_cached_json("typhoon_cache.json"))


@app.route("/api/stations")
def api_stations():
    """REST API endpoint for observation station dots."""
    return jsonify(load_cached_json("stations_cache.json"))


@app.route("/api/sync", methods=["POST", "GET"])
def api_sync():
    """API endpoint to trigger live CWA API ETL sync."""
    try:
        count = run_etl_pipeline()
        return jsonify({
            "status": "success",
            "count": count,
            "update_time": get_update_timestamp(),
            "message": "ETL sync completed successfully."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    ensure_db_ready()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
