"""
Database Service Module (Stage 3 implementation)
Handles SQLite database initialization, table creation (TemperatureForecasts),
non-duplicate data upserting (INSERT OR REPLACE), and SQL query validations.
"""

import os
import sqlite3
import logging
import pandas as pd
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# DEFAULT_DB_PATH is used as a fallback; the actual path is resolved at call time
# via get_db_path() so that Vercel's /tmp override (set via DB_PATH env var) works.
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_db_path() -> str:
    """Resolve the active DB path: honours DB_PATH env var, or falls back to /tmp/data.db on serverless environments."""
    if os.environ.get("DB_PATH"):
        return os.environ["DB_PATH"]
    
    # Auto-detect serverless / read-only environment
    default_dir = os.path.dirname(DEFAULT_DB_PATH)
    is_serverless = (
        os.environ.get("VERCEL") is not None
        or os.environ.get("VERCEL_ENV") is not None
        or (os.path.exists("/tmp") and not os.access(default_dir, os.W_OK))
    )
    
    if is_serverless and os.path.exists("/tmp"):
        tmp_path = "/tmp/data.db"
        if not os.path.exists(tmp_path) and os.path.exists(DEFAULT_DB_PATH):
            import shutil
            try:
                shutil.copy2(DEFAULT_DB_PATH, tmp_path)
            except Exception as e:
                logging.warning(f"Could not copy {DEFAULT_DB_PATH} to {tmp_path}: {e}")
        return tmp_path

    return DEFAULT_DB_PATH


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_path or get_db_path())
    return conn


def init_db(db_path: str = None) -> None:
    """
    Initialize SQLite database and create TemperatureForecasts table.
    Gracefully avoids writes if the table already exists.
    """
    db_path = db_path or get_db_path()
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TemperatureForecasts';")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(TemperatureForecasts);")
                cols = [c[1] for c in cursor.fetchall()]
                if "locationName" in cols:
                    return  # Table already valid, skip write
                cursor.execute("DROP TABLE TemperatureForecasts;")

            create_table_sql = """
            CREATE TABLE IF NOT EXISTS TemperatureForecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regionName TEXT NOT NULL,
                locationName TEXT NOT NULL,
                dataDate TEXT NOT NULL,
                mint REAL,
                maxt REAL,
                UNIQUE(locationName, dataDate)
            );
            """
            cursor.execute(create_table_sql)
            conn.commit()
        logging.info(f"Database initialized at: {db_path}")
    except sqlite3.OperationalError as e:
        logging.warning(f"init_db skipped write due to read-only storage: {e}")


def save_forecast_to_db(df: pd.DataFrame, db_path: str = None) -> int:
    """
    Save or update city-level weather forecast records into TemperatureForecasts.
    Uses INSERT OR REPLACE to ensure idempotency.

    Args:
        df (pd.DataFrame): DataFrame containing [regionName, locationName, dataDate, mint, maxt].
        db_path (str): Database file path.

    Returns:
        int: Number of rows inserted/updated.
    """
    db_path = db_path or get_db_path()
    if df.empty:
        logging.warning("Provided DataFrame is empty. Nothing saved to DB.")
        return 0

    init_db(db_path)

    upsert_sql = """
    INSERT OR REPLACE INTO TemperatureForecasts (regionName, locationName, dataDate, mint, maxt)
    VALUES (?, ?, ?, ?, ?);
    """

    records = [
        (row["regionName"], row["locationName"], str(row["dataDate"]), float(row["mint"]), float(row["maxt"]))
        for _, row in df.iterrows()
    ]

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(upsert_sql, records)
        conn.commit()

    logging.info(f"Successfully upserted {len(records)} city forecast records into TemperatureForecasts.")
    return len(records)


def query_distinct_regions(db_path: str = None) -> List[str]:
    """Query list of distinct region names from TemperatureForecasts."""
    db_path = db_path or get_db_path()
    init_db(db_path)
    sql = "SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY regionName;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
    return [r[0] for r in rows]


def query_distinct_cities(db_path: str = None) -> List[str]:
    """Query list of distinct county/city names from TemperatureForecasts."""
    db_path = db_path or get_db_path()
    init_db(db_path)
    sql = "SELECT DISTINCT locationName FROM TemperatureForecasts ORDER BY locationName;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
    return [r[0] for r in rows]


def query_forecast_by_city(city_name: str, db_path: str = None) -> pd.DataFrame:
    """Query weather forecast for a specific city/county."""
    db_path = db_path or get_db_path()
    init_db(db_path)
    sql = """
    SELECT id, regionName, locationName, dataDate, mint, maxt 
    FROM TemperatureForecasts 
    WHERE locationName = ? 
    ORDER BY dataDate ASC;
    """
    with get_connection(db_path) as conn:
        df = pd.read_sql_query(sql, conn, params=(city_name,))
    return df


def query_forecast_by_region(region_name: str, db_path: str = None) -> pd.DataFrame:
    """Query weather forecast for a specific region."""
    db_path = db_path or get_db_path()
    init_db(db_path)
    sql = """
    SELECT id, regionName, locationName, dataDate, mint, maxt 
    FROM TemperatureForecasts 
    WHERE regionName = ? 
    ORDER BY locationName, dataDate ASC;
    """
    with get_connection(db_path) as conn:
        df = pd.read_sql_query(sql, conn, params=(region_name,))
    return df


def query_all_forecasts(db_path: str = None) -> pd.DataFrame:
    """Query all forecast records from TemperatureForecasts."""
    db_path = db_path or get_db_path()
    init_db(db_path)
    sql = "SELECT id, regionName, locationName, dataDate, mint, maxt FROM TemperatureForecasts ORDER BY regionName, locationName, dataDate ASC;"
    with get_connection(db_path) as conn:
        df = pd.read_sql_query(sql, conn)
    return df


if __name__ == "__main__":
    from cwa_service import fetch_weather_forecast
    from data_processor import parse_weather_json, get_regional_forecast_df

    print("=== Stage 3 Test: SQLite Database & Upsert ===")
    
    # 1. Fetch & parse
    raw_json = fetch_weather_forecast()
    detailed_df = parse_weather_json(raw_json)
    regional_df = get_regional_forecast_df(detailed_df)

    # 2. Save to SQLite
    saved_count = save_forecast_to_db(regional_df)
    print(f"\n[DB] Saved {saved_count} records to SQLite database (data.db).")

    # 3. Test re-execution idempotency (prevent duplicate rows)
    saved_count_again = save_forecast_to_db(regional_df)
    print(f"[DB] Re-execution saved {saved_count_again} records (INSERT OR REPLACE tested).")

    # 4. SQL Verification (Unit 10)
    regions = query_distinct_regions()
    print(f"\n[SQL Query] Distinct Regions ({len(regions)}):", regions)

    test_region = "中部地區" if "中部地區" in regions else (regions[0] if regions else "北部地區")
    region_df = query_forecast_by_region(test_region)
    print(f"\n[SQL Query] Forecast for '{test_region}':")
    print(region_df)

    all_df = query_all_forecasts()
    print(f"\n[SQL Query] Total Records in DB: {len(all_df)}")
    print("\n[SUCCESS] Stage 3 SQLite Database & SQL validation completed!")
