import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

file_path = 'modified_dataset.csv'
df = pd.read_csv(file_path)

X = df.drop('WATER REQUIREMENT', axis=1)
y = df['WATER REQUIREMENT']

categorical_cols = X.select_dtypes(include=['object']).columns
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(), categorical_cols)
    ])

model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('regressor', RandomForestRegressor(random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")

rainy_conditions = X_test['WEATHER CONDITION'] == 'RAINY'
rainy_predictions = y_pred[rainy_conditions]
print(f"Average Water Requirement when Rainy: {rainy_predictions.mean()}")

model_filename = 'water_requirement_model.joblib'
joblib.dump(model, model_filename)
print(f"Model saved to {model_filename}")

def predict_water_requirement(new_data):
    """
    Predict water requirement for new data.
    
    Parameters:
    new_data (pd.DataFrame): DataFrame containing the same columns as the training data.
    
    Returns:
    np.ndarray: Predicted water requirement values.
    """
    return model.predict(new_data)

new_data = pd.DataFrame({
    'CROP TYPE': ['ONION'],
    'SOIL TYPE': ['WET'],
    'REGION': ['HUMID'],
    'WEATHER CONDITION': ['RAINY'],
    'temperature_min': [40],
    'temperature_max': [50]
})

predicted_water_requirement = predict_water_requirement(new_data)
print(f"Predicted Water Requirement: {predicted_water_requirement[0]}")
