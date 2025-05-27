import requests
from datetime import datetime, timezone, timedelta


OPENWEATHER_API_KEY = '55502a66a96823f0042a874dfcd8da1d'

def get_weather_data(city, units='metric'):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units={units}"
    res = requests.get(url)
    data = res.json()

    # Extraire sunrise et sunset en UTC (timestamp UNIX)
    print(data)
    sunrise_unix = data["city"]["sunrise"]
    sunset_unix = data["city"]["sunset"]

    # Convertir en format "HH:MM:SS"

# ...
    madagascar_tz=timezone(timedelta(hours=3))

    # Convertir en format "HH:MM:SS" avec datetime timezone-aware
    sunrise = datetime.fromtimestamp(sunrise_unix, tz=madagascar_tz).strftime("%H:%M:%S")
    sunset = datetime.fromtimestamp(sunset_unix, tz=madagascar_tz).strftime("%H:%M:%S")
# ...


    result = {"main": []}
    grouped_by_date = {}

    for entry in data['list']:
        dt_txt = entry['dt_txt']
        date, time = dt_txt.split()
        main = entry['main']
        weather = entry['weather'][0] if entry['weather'] else {}
        rain = entry.get('rain', {}).get('3h', 0.0)

        three_hour_entry = {
            "time": time,
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "rain": rain,
            "humidity": main.get("humidity")
        }

        if weather:
            three_hour_entry["description"] = weather.get("description")
            three_hour_entry["icon"] = weather.get("icon")

        if date not in grouped_by_date:
            grouped_by_date[date] = {
                "date": date,
                "sunrise": sunrise,
                "sunset": sunset,
                "three-hourly": []
            }

        grouped_by_date[date]["three-hourly"].append(three_hour_entry)

    result["main"] = list(grouped_by_date.values())
    print(f"NASANDRATRA : {result}")
    return result

# Exemple d'utilisation
city = "Fianarantsoa"
units = "metric"
weather_data = get_weather_data(city, units)

# # Affichage du résultat formaté
# import json
# print(json.dumps(weather_data, indent=4))
