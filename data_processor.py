"""
Data Processor Module (Stage 2 implementation)
Parses CWA JSON weather forecast data, extracts MinT/MaxT, maps regions, and cleans data into Pandas DataFrames.
"""

import logging
import pandas as pd
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Taiwan County to Region Mapping dictionary
COUNTY_TO_REGION = {
    "基隆市": "北部地區",
    "臺北市": "北部地區",
    "台北市": "北部地區",
    "新北市": "北部地區",
    "桃園市": "北部地區",
    "新竹市": "北部地區",
    "新竹縣": "北部地區",
    "宜蘭縣": "東北部地區",
    "苗栗縣": "中部地區",
    "臺中市": "中部地區",
    "台中市": "中部地區",
    "彰化縣": "中部地區",
    "南投縣": "中部地區",
    "雲林縣": "中部地區",
    "嘉義市": "南部地區",
    "嘉義縣": "南部地區",
    "臺南市": "南部地區",
    "台南市": "南部地區",
    "高雄市": "南部地區",
    "屏東縣": "南部地區",
    "花蓮縣": "東部地區",
    "臺東縣": "東南部地區",
    "台東縣": "東南部地區",
    "澎湖縣": "離島地區",
    "金門縣": "離島地區",
    "連江縣": "離島地區",
}


def map_county_to_region(location_name: str) -> str:
    """Map a Taiwan county/city name to its geographic region."""
    for county, region in COUNTY_TO_REGION.items():
        if county in location_name or location_name in county:
            return region
    return "其他地區"


def parse_weather_json(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parse CWA JSON weather response into a clean Pandas DataFrame (Unit 05, 06, 07).

    Args:
        json_data (dict): Raw JSON data from CWA API.

    Returns:
        pd.DataFrame: DataFrame containing [regionName, locationName, dataDate, mint, maxt].
    """
    records = json_data.get("records", {})
    locations = records.get("location", [])

    rows = []

    for loc in locations:
        location_name = loc.get("locationName", "")
        region_name = map_county_to_region(location_name)
        weather_elements = loc.get("weatherElement", [])

        # Extract MinT and MaxT element time arrays
        mint_times = []
        maxt_times = []

        for elem in weather_elements:
            elem_name = elem.get("elementName")
            if elem_name == "MinT":
                mint_times = elem.get("time", [])
            elif elem_name == "MaxT":
                maxt_times = elem.get("time", [])

        # Process MinT time entries
        time_data = {}
        for item in mint_times:
            start_time = item.get("startTime", "")
            date_str = start_time.split(" ")[0] if start_time else ""
            mint_val = item.get("parameter", {}).get("parameterName")
            if date_str and mint_val is not None:
                if date_str not in time_data:
                    time_data[date_str] = {}
                # Keep the minimum value if multiple time slots exist for the same date
                val = float(mint_val)
                if "mint" not in time_data[date_str] or val < time_data[date_str]["mint"]:
                    time_data[date_str]["mint"] = val

        # Process MaxT time entries
        for item in maxt_times:
            start_time = item.get("startTime", "")
            date_str = start_time.split(" ")[0] if start_time else ""
            maxt_val = item.get("parameter", {}).get("parameterName")
            if date_str and maxt_val is not None:
                if date_str not in time_data:
                    time_data[date_str] = {}
                # Keep the maximum value if multiple time slots exist for the same date
                val = float(maxt_val)
                if "maxt" not in time_data[date_str] or val > time_data[date_str]["maxt"]:
                    time_data[date_str]["maxt"] = val

        # Flatten into row records
        for date_str, temps in time_data.items():
            rows.append({
                "regionName": region_name,
                "locationName": location_name,
                "dataDate": date_str,
                "mint": temps.get("mint"),
                "maxt": temps.get("maxt")
            })

    df = pd.DataFrame(rows)

    # Data Cleaning (Unit 07)
    if not df.empty:
        df["mint"] = pd.to_numeric(df["mint"], errors="coerce")
        df["maxt"] = pd.to_numeric(df["maxt"], errors="coerce")
        df.dropna(subset=["mint", "maxt"], inplace=True)
        df.sort_values(by=["regionName", "locationName", "dataDate"], inplace=True)
        df.reset_index(drop=True, inplace=True)

    logging.info(f"Successfully parsed and cleaned weather data. Total records: {len(df)}")
    return df


def get_regional_forecast_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate county-level data into regional average/min-max forecast DataFrame.

    Args:
        df (pd.DataFrame): Detailed county-level weather DataFrame.

    Returns:
        pd.DataFrame: Regional aggregated DataFrame [regionName, dataDate, mint, maxt].
    """
    if df.empty:
        return pd.DataFrame(columns=["regionName", "dataDate", "mint", "maxt"])

    regional_df = df.groupby(["regionName", "dataDate"]).agg(
        mint=("mint", "min"),
        maxt=("maxt", "max")
    ).reset_index()

    regional_df.sort_values(by=["regionName", "dataDate"], inplace=True)
    regional_df.reset_index(drop=True, inplace=True)
    return regional_df


if __name__ == "__main__":
    from cwa_service import fetch_weather_forecast

    print("=== Stage 2 Test: JSON Parsing & Data Cleaning ===")
    raw_json = fetch_weather_forecast()
    
    # Unit 05 & 06: Parse JSON and extract MinT / MaxT
    detailed_df = parse_weather_json(raw_json)
    print("\n--- Detailed County Weather DataFrame (Top 10) ---")
    print(detailed_df.head(10))

    # Unit 07: Regional Aggregated DataFrame
    regional_df = get_regional_forecast_df(detailed_df)
    print("\n--- Regional Summary Weather DataFrame (Top 10) ---")
    print(regional_df.head(10))
    print(f"\nDataFrame Info:")
    print(regional_df.info())
    print("\n[SUCCESS] Stage 2 JSON Parsing and Data Cleaning completed!")
