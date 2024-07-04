import os
import requests
import json

json_file_path = os.path.join(os.path.dirname(__file__), 'req.json')

with open(json_file_path, 'r') as file:
    new_data = json.load(file)

url = 'http://127.0.0.1:5000/predict'

response = requests.post(url, json=new_data)

if response.status_code == 200:
    response_json = response.json()
    if response_json['status'] == 'success':
        data = response_json['data']
        print("Crop Title:", data['crop_title'])
        print("Soil Type:", data['soil_type'])
        print("Region:", data['region'])
        print("Weather Condition:", data['weather_condition'])
        print("Minimum Temperature:", data['temperature_min'])
        print("Maximum Temperature:", data['temperature_max'])
        print("Predicted Water Requirement:", data['predicted_water'])

        print("Crop ID:", data['crop_id'])
        print("Release Duration:", data['release_duration'])
        print("Time:", data['time'])  # Print time
        print("Next Irrigation:", data['next_irrigation'])  # Print next_irrigation
        print("Health:", data['health'])  # Print health
    else:
        print("Error:", response_json['error'])
