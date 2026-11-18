
import httpx
import time

MARINE_API = "https://marine-api.open-meteo.com/v1/marine"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

COASTAL_LOCATIONS = {
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "Goa": {"latitude": 15.2993, "longitude": 74.1240},
    "Chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "Kochi": {"latitude": 9.9312, "longitude": 76.2673},
    "Visakhapatnam": {"latitude": 17.6868, "longitude": 83.2185}
}

# Store successful responses for 15 minutes
CACHE_DURATION = 900
weather_cache = {}


async def get_marine_weather(location: str):

    if location not in COASTAL_LOCATIONS:
        raise ValueError(
            "Unsupported location. Choose Mumbai, Goa, Chennai, Kochi or Visakhapatnam."
        )

    # Check cache before calling external APIs
    cached = weather_cache.get(location)

    if cached and time.monotonic() - cached["time"] < CACHE_DURATION:
        return cached["data"]

    coordinates = COASTAL_LOCATIONS[location]

    marine_params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": (
            "wave_height,wave_direction,wave_period,"
            "sea_surface_temperature,ocean_current_velocity,"
            "ocean_current_direction"
        ),
        "daily": (
            "wave_height_max,wave_direction_dominant,wave_period_max"
        ),
        "forecast_days": 7,
        "timezone": "Asia/Kolkata",
        "cell_selection": "sea"
    }

    weather_params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "wind_speed_10m,wind_direction_10m,weather_code"
        ),
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }

    timeout = httpx.Timeout(20.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:

            marine_response = await client.get(
                MARINE_API, params=marine_params
            )
            marine_response.raise_for_status()

            weather_response = await client.get(
                WEATHER_API, params=weather_params
            )
            weather_response.raise_for_status()

            marine_data = marine_response.json()
            weather_data = weather_response.json()

        result = {
            "success": True,
            "project": "BlueWatch",
            "location": location,
            "coordinates": coordinates,
            "current_marine_conditions": marine_data.get("current", {}),
            "seven_day_marine_forecast": marine_data.get("daily", {}),
            "current_weather": weather_data.get("current", {}),
            "weather_units": weather_data.get("current_units", {})
        }

        # Save successful response in cache
        weather_cache[location] = {
            "time": time.monotonic(),
            "data": result
        }

        return result

    except httpx.HTTPStatusError as error:

        if error.response.status_code == 429:
            raise Exception(
                "Weather API rate limit reached. Please wait 15 minutes and try again."
            )

        raise Exception(
            f"Weather service error: HTTP {error.response.status_code}"
        )

    except httpx.RequestError:
        raise Exception(
            "Unable to connect to the weather service. Please try again later."
        )
