
# pip install openmeteo-requests
# pip install requests-cache retry-requests numpy pandas
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 47.0825,
	"longitude": 8.6357,
	"hourly": ["temperature_2m", "temperature_180m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "rain", "showers", "snowfall", "snow_depth", "precipitation", "precipitation_probability", "apparent_temperature", "dew_point_2m", "relative_humidity_2m", "is_day", "sunshine_duration"],
	"models": "best_match",
	"past_days": 0,
	"forecast_days": 1,
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_temperature_180m = hourly.Variables(1).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
hourly_cloud_cover_low = hourly.Variables(3).ValuesAsNumpy()
hourly_cloud_cover_mid = hourly.Variables(4).ValuesAsNumpy()
hourly_cloud_cover_high = hourly.Variables(5).ValuesAsNumpy()
hourly_visibility = hourly.Variables(6).ValuesAsNumpy()
hourly_rain = hourly.Variables(7).ValuesAsNumpy()
hourly_showers = hourly.Variables(8).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(9).ValuesAsNumpy()
hourly_snow_depth = hourly.Variables(10).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(11).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(12).ValuesAsNumpy()
hourly_apparent_temperature = hourly.Variables(13).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(14).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(15).ValuesAsNumpy()
hourly_is_day = hourly.Variables(16).ValuesAsNumpy()
hourly_sunshine_duration = hourly.Variables(17).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["temperature_180m"] = hourly_temperature_180m
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
hourly_data["visibility"] = hourly_visibility
hourly_data["rain"] = hourly_rain
hourly_data["showers"] = hourly_showers
hourly_data["snowfall"] = hourly_snowfall
hourly_data["snow_depth"] = hourly_snow_depth
hourly_data["precipitation"] = hourly_precipitation
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["apparent_temperature"] = hourly_apparent_temperature
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["is_day"] = hourly_is_day
hourly_data["sunshine_duration"] = hourly_sunshine_duration

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)
