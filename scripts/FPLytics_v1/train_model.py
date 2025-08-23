import joblib
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score


def run(): 
    master_training_df = pd.read_csv('../data/master_training_data.csv')

    print("Historical training data loaded successfully!")
    master_training_df.head()

    # --- Step 1: Define Your Features (X) and Target (y) ---
    target = 'event_points'
    features = [
        'now_cost', 'selected_by_percent', 'form', 'total_points', 'bonus', 'bps',
        'expected_goals_per_90', 'expected_assists_per_90', 'expected_goal_involvements_per_90',
        'expected_goals_conceded_per_90', 'influence', 'creativity', 'threat', 'ict_index',
        'team_elo', 'opponent_elo', 'is_home'
    ]
    model_df = master_training_df.dropna(subset=features + [target])

    # *** FIX: Convert the boolean 'is_home' column to integers (1s and 0s) ***
    model_df['is_home'] = model_df['is_home'].astype(int)

    X = model_df[features]
    y = model_df[target]

    # --- Step 2: Split the Data ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Step 3: Train the Model ---
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    print("Model training complete!")

    # --- Step 4: Evaluate the Model ---
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"\nModel Evaluation:")
    print(f"The model's predictions are off by an average of {mae:.2f} points.")


    # --- Calculate RMSE ---
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    print(f"RMSE (Root Mean Squared Error): {rmse:.2f} points")

    # --- Calculate R-Squared ---
    r2 = r2_score(y_test, predictions)
    print(f"R-Squared: {r2:.2f}")
    print(f"(This means our model explains {r2:.1%} of the variance in player points)")

    # Create a DataFrame of feature importances
    feature_importance_df = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    # Plot the feature importances
    plt.figure(figsize=(10, 8))
    sns.barplot(x='importance', y='feature', data=feature_importance_df)
    plt.title('XGBoost Feature Importance')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.show()

    # Define the path to save the model
    output_dir = '../../models'
    model_file = os.path.join(output_dir, 'fpl_model_v1.joblib')

    # Create the models directory in the root if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the trained model object to a file
    joblib.dump(model, model_file)

    print(f"Model successfully saved to '{model_file}'")