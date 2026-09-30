"""
Main Weather ETL Pipeline (Stages 1 - 3 Execution Script)
Orchestrates:
  1. Fetching raw JSON weather forecast from CWA Open Data API (Stage 1).
  2. Parsing and cleaning data into Pandas DataFrames (Stage 2).
  3. Upserting cleaned records into SQLite database (data.db) without duplicates (Stage 3).
"""

import os
import json
import logging
from datetime import datetime
from cwa_service import fetch_weather_forecast, fetch_station_observations, fetch_typhoon_data
from data_processor import parse_weather_json, parse_typhoon_data, parse_station_data
from database import save_forecast_to_db, query_all_forecasts

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CACHE_DIR = os.environ.get("CACHE_DIR", os.path.dirname(__file__))


def run_etl_pipeline() -> int:
    """Execute the full weather ETL pipeline including forecasts, stations, typhoons, and timestamps."""
    logging.info("Starting Weather ETL Pipeline...")
    
    # 1. Fetch raw API data (forecast, observations, typhoon)
    raw_json = fetch_weather_forecast()
    try:
        obs_json = fetch_station_observations()
    except Exception as e:
        logging.warning(f"Failed to fetch station observations: {e}")
        obs_json = {}

    try:
        ty_json = fetch_typhoon_data()
    except Exception as e:
        logging.warning(f"Failed to fetch typhoon data: {e}")
        ty_json = {}
    
    # 2. Parse & clean county/city-level forecast data
    detailed_df = parse_weather_json(raw_json, obs_json)
    
    # 3. Save / Upsert city-level records to SQLite
    saved_count = save_forecast_to_db(detailed_df)

    # 4. Cache typhoon tracks and station locations
    try:
        ty_list = parse_typhoon_data(ty_json)
        with open(os.path.join(CACHE_DIR, "typhoon_cache.json"), "w", encoding="utf-8") as f:
            json.dump(ty_list, f, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"Failed to cache typhoon data: {e}")

    try:
        st_list = parse_station_data(obs_json)
        with open(os.path.join(CACHE_DIR, "stations_cache.json"), "w", encoding="utf-8") as f:
            json.dump(st_list, f, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"Failed to cache stations data: {e}")

    # 5. Timestamp
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(os.path.join(CACHE_DIR, "update_time.txt"), "w", encoding="utf-8") as f:
            f.write(now_str)
    except Exception:
        pass
    
    logging.info(f"ETL Pipeline completed successfully! Total {saved_count} city records processed at {now_str}.")
    return saved_count


if __name__ == "__main__":
    count = run_etl_pipeline()
    df = query_all_forecasts()
    print(f"\n=== ETL Summary ===")
    print(f"Upserted Records: {count}")
    print(f"Total Database Rows: {len(df)}")
    print(df)
