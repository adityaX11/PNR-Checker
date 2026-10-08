import os
import time
import requests
import streamlit as st

# -----------------------------
# API Endpoints
# -----------------------------
PNR_BASE_URL = "https://irctc-indian-railway-pnr-status.p.rapidapi.com/getPNRStatus/"
TRAINS_BETWEEN_URL = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
SEARCH_STATION_URL = "https://irctc1.p.rapidapi.com/api/v1/searchStation"
GET_FARE_URL = "https://irctc1.p.rapidapi.com/api/v1/getFare"


# -----------------------------
# KEY ROTATION & POOL MANAGER
# -----------------------------
def get_api_key_pool() -> list[str]:
    """
    Retrieve all configured RapidAPI keys from Streamlit secrets
    or environment variables.

    Supports:
      1. Single string: RAPID_API_KEY = "key1"
      2. Comma-separated: RAPID_API_KEY = "key1, key2, key3"
      3. List of strings: RAPID_API_KEYS = ["key1", "key2", "key3"]
    """
    keys: list[str] = []

    # Check RAPID_API_KEYS (list or string in secrets)
    try:
        if "RAPID_API_KEYS" in st.secrets:
            val = st.secrets["RAPID_API_KEYS"]
            if isinstance(val, list):
                keys.extend([str(k).strip() for k in val if str(k).strip()])
            elif isinstance(val, str):
                keys.extend([k.strip() for k in val.split(",") if k.strip()])
    except Exception:
        pass

    # Check RAPID_API_KEY (single or comma-separated in secrets)
    try:
        if "RAPID_API_KEY" in st.secrets:
            val = st.secrets["RAPID_API_KEY"]
            if isinstance(val, list):
                keys.extend([str(k).strip() for k in val if str(k).strip()])
            elif isinstance(val, str):
                keys.extend([k.strip() for k in val.split(",") if k.strip()])
    except Exception:
        pass

    # Check OS environment variables as fallback
    env_key = os.environ.get("RAPID_API_KEY", "") or os.environ.get("RAPID_API_KEYS", "")
    if env_key:
        keys.extend([k.strip() for k in env_key.split(",") if k.strip()])

    # Deduplicate while preserving order
    unique_keys = []
    for k in keys:
        if k and k not in unique_keys:
            unique_keys.append(k)

    return unique_keys


def make_request_with_key_rotation(
    url: str,
    host: str,
    params: dict | None = None,
    timeout: int = 20,
) -> tuple[dict | None, str | None]:
    """
    Executes an HTTP GET request with automatic key rotation.
    If a key returns HTTP 429 (Rate Limit Exceeded) or HTTP 403 (quota exhausted),
    it immediately falls back to the next available key in the pool.
    """
    keys = get_api_key_pool()

    if not keys:
        return None, (
            "No RapidAPI key found! Please configure `RAPID_API_KEY` in "
            "`.streamlit/secrets.toml` or Streamlit Cloud Settings."
        )

    last_error = None
    rate_limited_count = 0

    for idx, key in enumerate(keys):
        headers = {
            "x-rapidapi-key": key,
            "x-rapidapi-host": host,
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)

            # 429: Too Many Requests (Rate limit hit)
            # 403: Forbidden / Quota exceeded for this month
            if response.status_code in (429, 403):
                rate_limited_count += 1
                last_error = f"API Key #{idx + 1} reached quota/rate limit (HTTP {response.status_code})."
                # If there are more keys, rotate immediately
                if idx < len(keys) - 1:
                    time.sleep(0.2)  # Tiny pause before rotating
                    continue
                else:
                    break

            # 401: Invalid key format
            if response.status_code == 401:
                last_error = f"API Key #{idx + 1} is invalid or unauthorized."
                if idx < len(keys) - 1:
                    continue
                break

            response.raise_for_status()
            json_data = response.json()
            return json_data, None

        except requests.exceptions.Timeout:
            last_error = "Railway API request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return None, "Network connection error. Please check your internet connectivity."
        except requests.exceptions.RequestException as e:
            last_error = f"Network error: {str(e)}"
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"

    # If all keys were rate limited
    if rate_limited_count == len(keys):
        return None, (
            f"All {len(keys)} configured RapidAPI key(s) have reached their daily/monthly limit. "
            "Please try again after quota reset or add another key to the pool."
        )

    return None, (last_error or "Unable to retrieve data from railway API.")


# -----------------------------
# 1. PNR STATUS (Smart Caching: 10 mins TTL)
# -----------------------------
@st.cache_data(show_spinner=False, ttl=600)
def get_pnr_status(pnr: str):
    """
    Fetch PNR Status with automatic key failover and 10-minute caching.
    """
    clean_pnr = str(pnr).strip()
    url = f"{PNR_BASE_URL}{clean_pnr}"
    host = "irctc-indian-railway-pnr-status.p.rapidapi.com"

    json_data, err = make_request_with_key_rotation(url=url, host=host, timeout=20)

    if err:
        return None, err

    if isinstance(json_data, dict):
        if json_data.get("success") is True and "data" in json_data:
            return json_data.get("data"), None
        elif json_data.get("success") is False:
            msg = json_data.get("message") or json_data.get("userMessage") or "Unable to fetch PNR status."
            return None, msg
        elif "pnrNumber" in json_data or "passengerList" in json_data:
            return json_data, None
        elif "data" in json_data and isinstance(json_data["data"], dict):
            return json_data["data"], None

    return None, "Unexpected response structure from railway API."


# -----------------------------
# 2. TRAINS BETWEEN STATIONS (Smart Caching: 12 Hours TTL)
# -----------------------------
@st.cache_data(show_spinner=False, ttl=43200)
def get_trains_between_stations(from_station: str, to_station: str, journey_date: str):
    """
    Fetch all direct trains between two stations.
    Cached for 12 hours (43,200s) because timetable schedules remain identical throughout the day,
    eliminating redundant API calls when multiple users search the same popular routes.
    """
    host = "irctc1.p.rapidapi.com"
    params = {
        "fromStationCode": from_station.strip().upper(),
        "toStationCode": to_station.strip().upper(),
        "dateOfJourney": journey_date.strip(),
    }

    json_data, err = make_request_with_key_rotation(
        url=TRAINS_BETWEEN_URL,
        host=host,
        params=params,
        timeout=20,
    )

    if err:
        return None, err

    if isinstance(json_data, dict):
        if json_data.get("status") is True and "data" in json_data:
            trains = json_data.get("data")
            if isinstance(trains, list):
                return trains, None
            return [], None
        else:
            msg = json_data.get("message") or "No trains found between selected stations."
            return [], msg

    return [], "Invalid response from train schedule service."


# -----------------------------
# 3. GET BERTH FARES (Smart Caching: 6 Hours TTL)
# -----------------------------
@st.cache_data(show_spinner=False, ttl=21600)
def get_train_fare(train_no: str, from_station: str, to_station: str):
    """
    Fetch official fare breakdown for all available classes (SL, 3A, 2A, 1A).
    Cached for 6 hours (21,600s) to prevent burning API calls on repeat fare checks.
    """
    host = "irctc1.p.rapidapi.com"
    params = {
        "trainNo": str(train_no).strip(),
        "fromStationCode": str(from_station).strip().upper(),
        "toStationCode": str(to_station).strip().upper(),
    }

    json_data, err = make_request_with_key_rotation(
        url=GET_FARE_URL,
        host=host,
        params=params,
        timeout=15,
    )

    if err:
        return None, err

    if isinstance(json_data, dict):
        if json_data.get("status") is True and "data" in json_data:
            return json_data.get("data"), None
        return None, json_data.get("message", "Fare data unavailable")

    return None, "Unexpected fare data format."


# -----------------------------
# 4. SEARCH STATIONS (Smart Caching: 24 Hours TTL)
# -----------------------------
@st.cache_data(show_spinner=False, ttl=86400)
def search_stations(query: str):
    """
    Search stations by city or name query via API.
    Cached for 24 hours.
    """
    if not query or len(query.strip()) < 2:
        return []

    host = "irctc1.p.rapidapi.com"
    params = {"query": query.strip()}

    json_data, _ = make_request_with_key_rotation(
        url=SEARCH_STATION_URL,
        host=host,
        params=params,
        timeout=10,
    )

    if isinstance(json_data, dict) and json_data.get("status") is True and isinstance(json_data.get("data"), list):
        return json_data["data"]
    return []