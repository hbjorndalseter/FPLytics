# main.py
import argparse
from scripts import build_historical_data, train_model, generate_predictions, suggest_transfers

def main():
    parser = argparse.ArgumentParser(description="FPL AI Manager v1")
    parser.add_argument("--full-retrain", action="store_true", help="Run the full pipeline: build historical data and retrain the model.")
    parser.add_argument("--predict", action="store_true", help="Generate new predictions for the upcoming gameweek.")
    parser.add_argument("--suggest", action="store_true", help="Generate transfer suggestions based on the latest predictions.")
    
    args = parser.parse_args()

    if args.full_retrain:
        print("--- Running Full Retrain Pipeline ---")
        build_historical_data.run()
        train_model.run()
        print("--- Full Retrain Complete ---")
    
    if args.predict:
        print("--- Generating New Predictions ---")
        generate_predictions.run()
        print("--- Predictions Complete ---")

    if args.suggest:
        print("--- Generating Transfer Suggestions ---")
        suggest_transfers.run()
        print("--- Suggestions Complete ---")

if __name__ == "__main__":
    main()