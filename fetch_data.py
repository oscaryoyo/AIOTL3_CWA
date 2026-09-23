"""
Main Weather ETL Pipeline (Stages 1 - 3 Execution Script)
Orchestrates:
  1. Fetching raw JSON weather forecast from CWA Open Data API (Stage 1).
  2. Parsing and cleaning data into Pandas DataFrames (Stage 2).
  3. Upserting cleaned records into SQLite database (data.db) without duplicates (Stage 3).
"""

import logging
from cwa_service import fetch_weather_forecast
from data_processor import parse_weather_json, get_regional_forecast_df
from database import save_forecast_to_db, query_all_forecasts

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_etl_pipeline() -> int:
    """Execute the full weather ETL pipeline."""
    logging.info("Starting Weather ETL Pipeline...")
    
    # 1. Fetch raw API data
    raw_json = fetch_weather_forecast()
    
    # 2. Parse & clean
    detailed_df = parse_weather_json(raw_json)
    regional_df = get_regional_forecast_df(detailed_df)
    
    # 3. Save / Upsert to SQLite
    saved_count = save_forecast_to_db(regional_df)
    
    logging.info(f"ETL Pipeline completed successfully! Total {saved_count} regional forecast records processed.")
    return saved_count


if __name__ == "__main__":
    count = run_etl_pipeline()
    df = query_all_forecasts()
    print(f"\n=== ETL Summary ===")
    print(f"Upserted Records: {count}")
    print(f"Total Database Rows: {len(df)}")
    print(df)
