"""External Services & REST API Client (100% Free, Zero Keys Required)."""
import json
import requests
from typing import Dict, Any, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Zieork-Agent/2.0",
    "Accept": "application/json, text/plain, */*"
}

def call_rest_api(url: str, method: str = "GET", payload: Optional[Dict] = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Execute a generic HTTP request to a public REST API or webhook.
    """
    try:
        method = method.upper()
        if method == "POST":
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=timeout)
        elif method == "PUT":
            resp = requests.put(url, json=payload, headers=HEADERS, timeout=timeout)
        else:
            resp = requests.get(url, params=payload, headers=HEADERS, timeout=timeout)

        # Parse JSON or text
        try:
            data = resp.json()
        except Exception:
            data = resp.text[:2000]

        return {
            "success": resp.status_code < 400,
            "status_code": resp.status_code,
            "url": url,
            "method": method,
            "data": data
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "url": url,
            "method": method,
            "error": str(e)
        }

def get_weather_forecast(city_or_lat: str = "San Francisco", lat: float = 37.7749, lon: float = -122.4194) -> Dict[str, Any]:
    """Fetch current weather via Open-Meteo (Free, No Auth)."""
    # Geocoding if city name provided
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_or_lat}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, headers=HEADERS, timeout=6).json()
        if geo_res.get("results"):
            target = geo_res["results"][0]
            lat = target["latitude"]
            lon = target["longitude"]
            city_or_lat = f"{target.get('name')}, {target.get('country', '')}"
    except Exception:
        pass

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    res = call_rest_api(url)
    if res["success"] and isinstance(res["data"], dict):
        weather = res["data"].get("current_weather", {})
        return {
            "location": city_or_lat,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": weather.get("temperature"),
            "windspeed_kmh": weather.get("windspeed"),
            "weathercode": weather.get("weathercode"),
            "time": weather.get("time")
        }
    return {"error": "Unable to fetch weather data."}

def get_crypto_price(coin_id: str = "bitcoin") -> Dict[str, Any]:
    """Fetch live crypto price via CoinGecko or CoinCap public API."""
    coin_clean = coin_id.lower().strip().replace(" ", "-")
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_clean}&vs_currencies=usd&include_24hr_change=true"
    res = call_rest_api(url)
    if res["success"] and isinstance(res["data"], dict) and coin_clean in res["data"]:
        info = res["data"][coin_clean]
        return {
            "coin": coin_clean,
            "price_usd": info.get("usd"),
            "change_24h": round(info.get("usd_24h_change", 0), 2)
        }
    # Fallback to coincap
    try:
        cc_url = f"https://api.coincap.io/v2/assets/{coin_clean}"
        cc_res = requests.get(cc_url, headers=HEADERS, timeout=6).json()
        if "data" in cc_res:
            d = cc_res["data"]
            return {
                "coin": coin_clean,
                "price_usd": round(float(d.get("priceUsd", 0)), 2),
                "change_24h": round(float(d.get("changePercent24Hr", 0)), 2)
            }
    except Exception:
        pass
    return {"error": f"Could not find crypto price for '{coin_id}'"}
