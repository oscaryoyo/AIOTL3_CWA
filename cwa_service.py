"""
CWA Open Data API Service (Stage 1 implementation)
Handles environment setup, API Key loading, and fetching weather data from CWA Open Data API.
"""

import os
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

# CWA API Configuration
CWA_API_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
DEFAULT_DATASET_ID = "F-C0032-001"  # 今明36小時天氣預報


def get_cwa_api_key() -> str:
    """Retrieve CWA API key from environment variables."""
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        raise ValueError("Error: CWA_API_KEY is not set in environment or .env file.")
    return api_key


def fetch_weather_forecast(dataset_id: str = DEFAULT_DATASET_ID) -> dict:
    """
    Fetch weather forecast data from CWA Open Data API.
    
    Args:
        dataset_id (str): The CWA dataset ID (default: 'F-C0032-001').

    Returns:
        dict: Parsed JSON response dictionary.
    """
    api_key = get_cwa_api_key()
    url = f"{CWA_API_BASE_URL}/{dataset_id}"
    params = {
        "Authorization": api_key,
        "format": "JSON"
    }

    logging.info(f"Connecting to CWA API dataset: {dataset_id}...")
    
    try:
        # Try standard requests with SSL verification
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.SSLError:
        logging.warning("SSL Certificate Verification failed. Retrying without SSL verification...")
        # Fallback for environments with local SSL cert store issues
        response = requests.get(url, params=params, verify=False, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from CWA API: {e}")
        raise

    data = response.json()
    if not data.get("success") == "true" and not data.get("success") is True:
        raise ValueError(f"CWA API returned unsuccessful response: {data}")

    logging.info("Successfully fetched weather forecast data from CWA API.")
    return data


if __name__ == "__main__":
    print("=== Stage 1 Test: CWA API Data Acquisition ===")
    try:
        weather_json = fetch_weather_forecast()
        records = weather_json.get("records", {})
        dataset_name = records.get("datasetDescription", "天氣預報")
        locations = records.get("location", [])
        
        print(f"Dataset: {dataset_name}")
        print(f"Total Locations Fetched: {len(locations)}")
        print("Sample Locations:")
        for loc in locations[:5]:
            print(f"  - {loc.get('locationName')}")
        print("\n[SUCCESS] Stage 1 API Data Acquisition completed!")
    except Exception as err:
        print(f"[ERROR] Stage 1 failed: {err}")
