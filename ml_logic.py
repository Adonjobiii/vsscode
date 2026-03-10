# ml_logic.py

import os
import sys
import re
import warnings
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Suppress sklearn model version mismatch warnings from cached .joblib files
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

# Import necessary constants and data from the config file
from config_data import (
    APTITUDE_MODEL_CATEGORIES, DUMMY_QUESTIONS, DUMMY_CORRECT_ANSWERS,
    X_data_train_aptitude, y_labels_train_aptitude, 
    X_data_train_career, y_labels_train_career,
    MONGODB_TIMEOUT_MS, CONNECTION_STRING, db
)

# --- GLOBAL TRAIN/TEST SPLIT DEFINITION (CRITICAL FOR MODULE SCOPE) ---
# This block uses the full arrays imported from config_data and splits them once.

# Aptitude Split (8 samples for training/CV, 1 for final test)
# Stratification is ideally used but omitted here for simplicity with test_size=1
X_train_aptitude, X_test_aptitude, y_train_aptitude, y_test_aptitude = \
    train_test_split(X_data_train_aptitude, y_labels_train_aptitude, test_size=1, random_state=42)

# Career Split (20% for testing)
X_train_career, X_test_career, y_train_career, y_test_career = \
    train_test_split(X_data_train_career, y_labels_train_career, test_size=0.2, random_state=42)


# --- DATA PROCESSOR CLASS ---
class DataProcessor:
    def __init__(self):
        # Initialize with DUMMY data as fallback
        self.QUESTIONS = DUMMY_QUESTIONS
        self.CORRECT_ANSWERS = DUMMY_CORRECT_ANSWERS
        self.BOOM_PERCENTAGE_DATA = self._calculate_boom_percentage()
        
        # Call the loader, which handles its own MongoDB checks
        self._load_aptitude_data()

    def _load_aptitude_data(self):
        # Load from local JSON file instead of empty MongoDB collection
        import json
        import os
        from collections import defaultdict
        
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
        ans_file = os.path.join(os.path.dirname(__file__), 'data', 'correct_answers.json')
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                raw_qs = json.load(f)
            
            with open(ans_file, 'r', encoding='utf-8') as f:
                raw_ans = json.load(f)
                
            self.QUESTIONS = raw_qs
            self.CORRECT_ANSWERS = raw_ans
            print("\n[DATA] Aptitude bank: Loaded from local JSON database")
            
        except Exception as e:
            print(f"Error loading local aptitude JSON: {e}. Falling back to DUMMY data.")
            self.QUESTIONS = DUMMY_QUESTIONS
            self.CORRECT_ANSWERS = DUMMY_CORRECT_ANSWERS

    def _calculate_boom_percentage(self):
        # SIMULATED DATA
        data = {
            'Rank': [61, 72, 500, 1200, 3000, 4500, 6000, 8000, 10000, 12000, 15000, 52473],
            'Course': [
                'CS-Computer Science & Engineering', 'EC-Electronics & Communication', 'CS-Computer Science & Engineering',
                'EE-Electrical & Electronics Engineering', 'ME-Mechanical Engineering', 'CE-Civil Engineering',
                'IT-Information Technology', 'CH-Chemical Engineering', 'AE-Applied Electronics & Instrumentation',
                'EL-Electrical and Computer Engineering', 'IE-Industrial Engineering', 'BT-Biotechnology'
            ]
        }
        all_data = pd.DataFrame(data)

        all_data['Rank'] = pd.to_numeric(all_data['Rank'], errors='coerce')
        all_data.dropna(subset=['Rank', 'Course'], inplace=True)
        all_data['Course Code'] = all_data['Course'].apply(lambda x: re.match(r'^([A-Z]{2,3})-', str(x)).group(1) if re.match(r'^[A-Z]{2,3}-', str(x)) else None)
        all_data.dropna(subset=['Course Code'], inplace=True)

        closing_ranks = all_data.groupby('Course Code')['Rank'].max().reset_index()
        closing_ranks.rename(columns={'Rank': 'Last Rank'}, inplace=True)

        min_rank = all_data['Rank'].min()
        max_rank = all_data['Rank'].max()
        
        closing_ranks['Boom Percentage'] = (1 - (closing_ranks['Last Rank'] - min_rank) / (max_rank - min_rank)) * 100
        
        return pd.Series(closing_ranks['Boom Percentage'].values, index=closing_ranks['Course Code']).to_dict()

# --- ML MODEL TRAINER CLASS ---
class MLModelTrainer:
    MODEL_DIR = "models"
    
    def __init__(self):
        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR)
            
        self.career_model = self._load_or_train_career_model()
        self.aptitude_model = self._load_or_train_aptitude_model()
        self.retrain_threshold = 10 
        self.training_collection = db["training_data"] if db is not None else None

    def log_and_retrain_career(self, features, label, metadata=None):
        """Logs new data for career model to MongoDB and retrains if threshold met."""
        if self.training_collection is None:
            print("[ML] MongoDB not connected. Skipping log.")
            return

        record = {
            "type": "career",
            "features": features,
            "label": int(label),
            "timestamp": pd.Timestamp.now().isoformat(),
            "metadata": metadata or {}
        }
        self.training_collection.insert_one(record)
        
        # Check if we should retrain
        count = self.training_collection.count_documents({"type": "career"})
        if count % self.retrain_threshold == 0 and count > 0:
            print(f"Triggering automated retraining for Career Model ({count} total samples)...")
            all_records = list(self.training_collection.find({"type": "career"}))
            new_df = pd.DataFrame([{"features": r["features"], "label": r["label"]} for r in all_records])
            self._retrain_career_model(new_df)

    def log_and_retrain_aptitude(self, features, label, track="engineering", metadata=None):
        """Logs new data for aptitude model to MongoDB and retrains if threshold met."""
        if self.training_collection is None:
            return

        record = {
            "type": f"aptitude_{track}",
            "features": features,
            "label": int(label),
            "timestamp": pd.Timestamp.now().isoformat(),
            "metadata": metadata or {}
        }
        self.training_collection.insert_one(record)
        
        count = self.training_collection.count_documents({"type": f"aptitude_{track}"})
        if count % self.retrain_threshold == 0 and count > 0:
            print(f"Triggering automated retraining for {track.capitalize()} Aptitude Model ({count} total samples)...")
            all_records = list(self.training_collection.find({"type": f"aptitude_{track}"}))
            new_df = pd.DataFrame([{"features": r["features"], "label": r["label"]} for r in all_records])
            
            # For now, we mainly retrain the core Engineering model if track is 'engineering'
            # For other tracks, we log the data which prepared them for future model training
            if track == "engineering":
                self._retrain_aptitude_model(new_df)
            else:
                # Placeholder for other track-specific models
                print(f"Data logged for {track}. Track-specific model retraining coming soon.")

    def _retrain_career_model(self, new_data=None):
        path = os.path.join(self.MODEL_DIR, 'career_model.joblib')
        
        # Merge old and new data
        X_combined = X_train_career
        y_combined = y_train_career
        
        if new_data is not None:
            X_new = np.array(new_data["features"].tolist())
            y_new = np.array(new_data["label"].tolist())
            X_combined = np.vstack([X_combined, X_new])
            y_combined = np.concatenate([y_combined, y_new])
            
        print("Retraining Career Model...")
        model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_combined, y_combined)
        joblib.dump(model, path)
        self.career_model = model
        print("Career Model updated.")

    def _retrain_aptitude_model(self, new_data=None):
        path = os.path.join(self.MODEL_DIR, 'aptitude_model.joblib')
        
        X_combined = X_train_aptitude
        y_combined = y_train_aptitude
        
        if new_data is not None:
            X_new = np.array(new_data["features"].tolist())
            y_new = np.array(new_data["label"].tolist())
            X_combined = np.vstack([X_combined, X_new])
            y_combined = np.concatenate([y_combined, y_new])
            
        print("Retraining Aptitude Model...")
        model = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42)
        model.fit(X_combined, y_combined)
        joblib.dump(model, path)
        self.aptitude_model = model
        print("Aptitude Model updated.")

    def _load_or_train_career_model(self):
        path = os.path.join(self.MODEL_DIR, 'career_model.joblib')
        if os.path.exists(path):
            print("Loading existing Career Model.")
            return joblib.load(path)
        
        print("Training Career Model...")
        
        param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 7]}
        # Use the SPLIT TRAINING data for GridSearchCV
        grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, scoring='accuracy')
        grid_search.fit(X_train_career, y_train_career) # Using the larger train split for CV
        
        model = grid_search.best_estimator_
        
        # Calculate final accuracy on the held-out TEST set
        test_accuracy = model.score(X_test_career, y_test_career)
        print(f"Career Model Test Accuracy (on held-out data): {test_accuracy:.4f}")
        
        joblib.dump(model, path)
        print(f"Career Model trained (Best Params: {grid_search.best_params_}) and saved.")
        return model

    def _load_or_train_aptitude_model(self):
        path = os.path.join(self.MODEL_DIR, 'aptitude_model.joblib')
        if os.path.exists(path):
            print("Loading existing Aptitude Model.")
            return joblib.load(path)

        print("Training Aptitude Model with Hyperparameter Tuning...")
        
        # 1. Define the base model
        base_model = RandomForestClassifier(random_state=42)

        # 2. Define the parameter grid to search
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, None],
            'min_samples_split': [2, 5],
        }

        # 3. Perform Grid Search with Cross-Validation
        try:
            # Use the SPLIT TRAINING data for GridSearchCV
            # cv=2 is used as X_train_aptitude has only 8 samples (with some repeating classes)
            grid_search = GridSearchCV(base_model, param_grid, cv=2, scoring='accuracy', n_jobs=-1) 
            grid_search.fit(X_train_aptitude, y_train_aptitude)
            model = grid_search.best_estimator_
            print(f"Hyperparameter search complete. Best parameters found: {grid_search.best_params_}")
            
        except ValueError:
            # Fallback if CV fails due to data constraints
            print("CV failed due to small dataset size. Training with default parameters (n_estimators=100).")
            # Fit the model using the training split, not the whole dataset
            model = base_model.fit(X_train_aptitude, y_train_aptitude)
            
        # Calculate final accuracy on the held-out TEST set
        test_accuracy = model.score(X_test_aptitude, y_test_aptitude)
        print(f"Aptitude Model Test Accuracy (on held-out data): {test_accuracy:.4f}")

        joblib.dump(model, path)
        print("Aptitude Model trained and saved.")
        return model