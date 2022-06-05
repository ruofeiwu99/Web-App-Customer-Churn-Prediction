#!/usr/bin/env bash

# Acquire data from URL
python3 run.py acquire_data

# Generate clean data set
python3 run.py clean_data

# Train model
python3 run.py train_model

# Produce predictions
python3 run.py predict

# Model evaluation
python3 run.py evaluate