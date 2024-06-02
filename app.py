from flask import Flask, request, jsonify
import joblib
import pandas as pd
import requests

app = Flask(__name__)

model_water_filename = 'water_requirement_model.joblib'
model_water = joblib.load(model_water_filename)

# Map moisture values to moisture conditions
def get_soil_type(moisture):
    if moisture > 45:
        return "wet"
    elif 25 < moisture <= 45:
        return "humid"
    elif moisture <= 25:
        return "dry"
    else:
        return "humid"
    
def get_region(moisture):
    if 10 > moisture :
        return "desert"
    elif 10 < moisture <= 20:
        return "semi arid"
    elif 20 < moisture <= 40:
        return "semi humid"
    elif 40 < moisture <= 70:
        return "humid"
    else:
        return "semi humid"

 # Map weather codes to weather conditions
def get_weather_condition(weather_code, precipitation):
    if weather_code in [ 61, 63, 65, 66, 67, 73, 75, 80, 81, 82, 85, 86, 95, 96, 99] and precipitation > 60:
        return "rainy"
    elif weather_code in [0, 1]:
        return "sunny"
    else:
        return "normal"

def get_health_status(moisture):
    if 15 > moisture:
        return "poor"
    elif 15 < moisture <= 25:
        return "needs_attention"
    else:
        return "healthy"

# Crop ID mapping
crop_id_mapping = {
    'BANANA': 0,
    'SOYABEAN': 1,
    'CABBAGE': 2,
    'POTATO': 3,
    'RICE': 4,
    'MELON': 5,
    'MAIZE': 6,
    'CITRUS': 7,
    'BEAN': 8,
    'WHEAT': 9,
    'MUSTARD': 10,
    'COTTON': 11,
    'SUGARCANE': 12,
    'TOMATO': 13,
    'ONION': 14,
}

# Endpoint for predicting moisture and water requirement
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Crop Label
    crop_title = data["crop"]["type"]
    crop_id = crop_id_mapping.get(crop_title.upper(), 0) 

    next_irrigation = data["crop"]["next_irrigation"]

    # Extract current time
    current_time = data["weather"]["current"]["time"]

     # Extract and process moisture data
    moisture_readings = [reading["moisture"] for reading in data["readings"]]
    mean_moisture = sum(moisture_readings) / len(moisture_readings) if moisture_readings else 0
    
    soil_type = get_soil_type(mean_moisture)
    region = get_region(mean_moisture)

    precipitation = data["weather"]["current"]["precipitation"]
    
    # Find weather code for current time
    weather_code = None
    for hour in data["weather"]["hourly"]:
        if hour["time"] == current_time:
            weather_code = hour["weatherCode"]
            break
    
    # Set weather condition directly from the function result
    weather_condition = get_weather_condition(weather_code,precipitation)  # Assuming first code is representative

    # Extract temperatures from hourly data
    hourly_temperatures = [hour["temperature2m"] for hour in data["weather"]["hourly"]]
    
    # Find lowest and highest temperatures
    temperature_min = min(hourly_temperatures)
    temperature_max = max(hourly_temperatures)
    
    # Create a DataFrame with temperature values
    df_predict = pd.DataFrame({
    'CROP TYPE': [crop_title.upper()],
    'SOIL TYPE': [soil_type.upper()],
    'REGION': [region.upper()],
    'WEATHER CONDITION': [weather_condition.upper()],
    'temperature_min': [temperature_min],
    'temperature_max': [temperature_max]
    })
    
    # Predict water requirement
    predicted_water = model_water.predict(df_predict)
    release_duration = predicted_water / 2  # Assuming constant release rate of 2 liters per minute
    health_status= get_health_status(mean_moisture)

    # Prepare response data
    response_data = {
        'crop_title': crop_title,
        'soil_type': soil_type,
        'region': region,
        'weather_condition': weather_condition,
        'temperature_min': temperature_min,
        'temperature_max': temperature_max,
        'predicted_water': predicted_water.tolist(),
        
        'crop_id': crop_id,
        'time': current_time,
        'next_irrigation': next_irrigation,
        'release_duration': release_duration.tolist(),
        'health': health_status,
    }

    # Send the response back to Server B
    # response_url = "http://localhost:5001/receive_prediction" testing localhost url server
    response_url = "https://farm.dijinx.com/api/v1/farm/predictor/result"    
    response = requests.post(response_url, json=response_data)

    if response.status_code == 200:
        return jsonify({'status': 'success', 'data': response_data})
    else:
        return jsonify({'status': 'failure', 'error': response.text}), response.status_code

if __name__ == '__main__':
    app.run(port=5000, debug=True)