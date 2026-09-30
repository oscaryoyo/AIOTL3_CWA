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


def parse_weather_json(json_data: Dict[str, Any], obs_data: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Parse CWA JSON weather forecast response and optional station observations into a rich Pandas DataFrame.

    Args:
        json_data (dict): Raw JSON forecast data from CWA API (F-C0032-001).
        obs_data (dict, optional): Real-time station observations from CWA API (O-A0003-001).

    Returns:
        pd.DataFrame: DataFrame containing [regionName, locationName, dataDate, mint, maxt, wx, pop, ci, windSpeed, windDirection, humidity, precipitation].
    """
    records = json_data.get("records", {})
    locations = records.get("location", [])

    # Process county observation data if provided
    county_obs = {}
    if obs_data:
        for s in obs_data.get("records", {}).get("Station", []):
            c = s.get("GeoInfo", {}).get("CountyName")
            if c and c not in county_obs:
                we = s.get("WeatherElement", {})
                try:
                    temp = float(we.get("AirTemperature", 26))
                except (ValueError, TypeError):
                    temp = 26.0
                try:
                    humid = float(we.get("RelativeHumidity", 72))
                except (ValueError, TypeError):
                    humid = 72.0
                try:
                    ws = float(we.get("WindSpeed", 2.2))
                except (ValueError, TypeError):
                    ws = 2.2
                try:
                    wd = float(we.get("WindDirection", 45))
                except (ValueError, TypeError):
                    wd = 45.0
                try:
                    precip = float(we.get("Now", {}).get("Precipitation", 0))
                except (ValueError, TypeError):
                    precip = 0.0

                county_obs[c] = {
                    "temp": temp if temp > -50 else 26.0,
                    "humidity": humid if humid > 0 else 72.0,
                    "windSpeed": ws if ws >= 0 else 2.0,
                    "windDirection": wd,
                    "precipitation": precip if precip >= 0 else 0.0,
                    "weather": we.get("Weather", "多雲")
                }

    rows = []

    for loc in locations:
        location_name = loc.get("locationName", "")
        region_name = map_county_to_region(location_name)
        weather_elements = loc.get("weatherElement", [])

        # Map element time arrays
        elem_dict = {}
        for elem in weather_elements:
            elem_dict[elem.get("elementName")] = elem.get("time", [])

        mint_times = elem_dict.get("MinT", [])
        maxt_times = elem_dict.get("MaxT", [])
        wx_times = elem_dict.get("Wx", [])
        pop_times = elem_dict.get("PoP", [])
        ci_times = elem_dict.get("CI", [])

        # Aggregate data by date
        time_data = {}

        # 1. MinT
        for item in mint_times:
            date_str = item.get("startTime", "").split(" ")[0]
            val = item.get("parameter", {}).get("parameterName")
            if date_str and val is not None:
                if date_str not in time_data:
                    time_data[date_str] = {}
                v = float(val)
                if "mint" not in time_data[date_str] or v < time_data[date_str]["mint"]:
                    time_data[date_str]["mint"] = v

        # 2. MaxT
        for item in maxt_times:
            date_str = item.get("startTime", "").split(" ")[0]
            val = item.get("parameter", {}).get("parameterName")
            if date_str and val is not None:
                if date_str not in time_data:
                    time_data[date_str] = {}
                v = float(val)
                if "maxt" not in time_data[date_str] or v > time_data[date_str]["maxt"]:
                    time_data[date_str]["maxt"] = v

        # 3. Wx (Weather condition)
        for item in wx_times:
            date_str = item.get("startTime", "").split(" ")[0]
            val = item.get("parameter", {}).get("parameterName")
            if date_str and val and date_str in time_data:
                if "wx" not in time_data[date_str]:
                    time_data[date_str]["wx"] = str(val)

        # 4. PoP (Precipitation probability)
        for item in pop_times:
            date_str = item.get("startTime", "").split(" ")[0]
            val = item.get("parameter", {}).get("parameterName")
            if date_str and val and date_str in time_data:
                if "pop" not in time_data[date_str]:
                    time_data[date_str]["pop"] = str(val)

        # 5. CI (Comfort index)
        for item in ci_times:
            date_str = item.get("startTime", "").split(" ")[0]
            val = item.get("parameter", {}).get("parameterName")
            if date_str and val and date_str in time_data:
                if "ci" not in time_data[date_str]:
                    time_data[date_str]["ci"] = str(val)

        # Observation data for this county
        obs = county_obs.get(location_name, {
            "windSpeed": 2.5,
            "windDirection": 60.0,
            "humidity": 70.0,
            "precipitation": 0.0,
            "weather": "多雲"
        })

        # Flatten into rows
        for date_str, temps in time_data.items():
            rows.append({
                "regionName": region_name,
                "locationName": location_name,
                "dataDate": date_str,
                "mint": temps.get("mint"),
                "maxt": temps.get("maxt"),
                "wx": temps.get("wx", obs.get("weather", "多雲")),
                "pop": temps.get("pop", "20"),
                "ci": temps.get("ci", "舒適"),
                "windSpeed": obs.get("windSpeed", 2.5),
                "windDirection": obs.get("windDirection", 60.0),
                "humidity": obs.get("humidity", 70.0),
                "precipitation": obs.get("precipitation", 0.0)
            })

    df = pd.DataFrame(rows)

    # Data Cleaning
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


def parse_typhoon_data(json_data: Dict[str, Any]) -> list:
    """Parse CWA tropical cyclone / typhoon forecast and past track data."""
    if not json_data:
        return []
    cyclones = json_data.get("records", {}).get("TropicalCyclones", {}).get("TropicalCyclone", [])
    results = []
    for c in cyclones:
        name = c.get("CwaTyphoonName") or c.get("TyphoonName") or (f"TD-{c.get('CwaTdNo', '')}")
        analysis = c.get("AnalysisData", {}).get("Fix", [])
        forecast = c.get("ForecastData", {}).get("Fix", [])
        past_pts = []
        for a in analysis:
            try:
                past_pts.append({
                    "lat": float(a.get("CoordinateLatitude")),
                    "lng": float(a.get("CoordinateLongitude")),
                    "time": a.get("DateTime", ""),
                    "wind": a.get("MaxWindSpeed", "--"),
                    "pressure": a.get("Pressure", "--"),
                    "speed": a.get("MovingSpeed", "--"),
                    "dir": a.get("MovingDirection", "")
                })
            except Exception:
                pass
        fc_pts = []
        for f in forecast:
            try:
                fc_pts.append({
                    "lat": float(f.get("CoordinateLatitude")),
                    "lng": float(f.get("CoordinateLongitude")),
                    "hour": f.get("ForecastHour", ""),
                    "wind": f.get("MaxWindSpeed", "--"),
                    "radius": float(f.get("Radius70PercentProbability", 0))
                })
            except Exception:
                pass
        results.append({
            "name": name,
            "typhoonNo": c.get("TyphoonNo") or c.get("CwaTdNo", ""),
            "past": past_pts,
            "forecast": fc_pts
        })
    return results


def parse_station_data(obs_data: Dict[str, Any]) -> list:
    """Parse real-time weather stations and coordinates into a list of station points."""
    if not obs_data:
        return []
    stations = obs_data.get("records", {}).get("Station", [])
    st_list = []
    for s in stations:
        name = s.get("StationName")
        county = s.get("GeoInfo", {}).get("CountyName", "")
        coords = s.get("GeoInfo", {}).get("Coordinates", [])
        lat, lon = None, None
        for co in coords:
            if co.get("CoordinateName") == "WGS84":
                try:
                    lat = float(co.get("StationLatitude"))
                    lon = float(co.get("StationLongitude"))
                except Exception:
                    pass
        if lat and lon:
            we = s.get("WeatherElement", {})
            st_list.append({
                "name": name,
                "county": county,
                "lat": lat,
                "lng": lon,
                "temp": we.get("AirTemperature", "--"),
                "humid": we.get("RelativeHumidity", "--"),
                "wind": we.get("WindSpeed", "--"),
                "rain": we.get("Now", {}).get("Precipitation", "--"),
                "wx": we.get("Weather", "--")
            })
    return st_list


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
