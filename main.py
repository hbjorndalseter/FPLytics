# main.py
import argparse
import sys
import os

# Add the scripts directory to the Python path
# This allows us to import our scripts
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'FPLytics_v1'))

from scripts import build_historical_data, train_model, generate_predictions, suggest_transfers

def main():
    parser = argparse.ArgumentParser(
        description="FPL AI Manager v1 - Your personal FPL assistant."
    )
    parser.add_argument(
        "--build-data", 
        action="store_true", 
        help="Build the historical training dataset from last season. (Run once)"
    )
    parser.add_argument(
        "--train", 
        action="store_true", 
        help="Train a new model using the historical dataset. (Run after building data)"
    )
    parser.add_argument(
        "--predict", 
        action="store_true", 
        help="Generate new player point predictions for the upcoming gameweek."
    )
    parser.add_argument(
        "--suggest", 
        action="store_true", 
        help="Generate optimal transfer suggestions for your team."
    )
    
    args = parser.parse_args()

    if args.build_data:
        build_historical_data.run()
    
    if args.train:
        train_model.run()

    if args.predict:
        generate_predictions.run()

    if args.suggest:
        suggest_transfers.run()

    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()