# ml_logic.py

import os
import sys
import re
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split 
from sklearn.metrics import accuracy_score 
import joblib 

# Import necessary constants and data from the config file
from config_data import (
    APTITUDE_MODEL_CATEGORIES, DUMMY_QUESTIONS, DUMMY_CORRECT_ANSWERS,
    X_data_train_aptitude, y_labels_train_aptitude, 
    X_data_train_career, y_labels_train_career,
    MONGODB_TIMEOUT_MS, CONNECTION_STRING
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
        # Check for PyMongo availability locally for robustness
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, OperationFailure
            MONGODB_IS_AVAILABLE_LOCAL = True
        except ImportError:
            MONGODB_IS_AVAILABLE_LOCAL = False
        
        if not MONGODB_IS_AVAILABLE_LOCAL:
            # If PyMongo is missing, we stick with the DUMMY data initialized in __init__
            print("Using dummy aptitude data (PyMongo missing or connection failed).")
            return

        try:
            # Attempt to establish connection with timeout
            client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS)
            client.admin.command('ismaster') # Validate the connection
            db = client['project']
            questions_collection = db.questions
            
            QUESTIONS_LIVE = defaultdict(list)
            CORRECT_ANSWERS_LIVE = defaultdict(dict)
            
            for doc in questions_collection.find({}):
                category = doc.get('category')
                q_id = doc.get('question_id')
                question_data = {"id": q_id, "q": doc.get('q'), "options": doc.get('options')}
                QUESTIONS_LIVE[category].append(question_data)
                CORRECT_ANSWERS_LIVE[category][q_id] = doc.get('correct_answer')
            
            # If successful, overwrite the dummy data
            self.QUESTIONS = dict(QUESTIONS_LIVE)
            self.CORRECT_ANSWERS = dict(CORRECT_ANSWERS_LIVE)
            print("Successfully loaded aptitude data from MongoDB.")
        
        except (ConnectionFailure, OperationFailure) as e:
            print(f"MongoDB Connection Failure: {e}. Using dummy data.")
        except Exception as e:
            print(f"An unexpected error occurred with MongoDB: {e}. Using dummy data.")

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