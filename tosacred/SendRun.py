import gc
import os
import pandas as pd
from sacred import Experiment
from sacred.observers import MongoObserver
import numpy as np
import pickle
from config import params as config


# Initialize a Sacred Experiment with the provided experiment name
ex = Experiment(config.run_name, save_git_info=False)

# Add a MongoObserver to the experiment for logging to MongoDB
ex.observers.append(MongoObserver(url=config.mongo_uri, db_name=config.db_name))

shared_data = {}


# Configuration function for the experiment
@ex.config
def cfg():
    experiment = ''


# Main function to run the experiment
@ex.automain
def run(_run):
    try:

        for val in shared_data['data']:
            _run.log_scalar(f'data', val)

        for val in shared_data['fit_data']:
            _run.log_scalar(f'run_data', val)

    finally:
        print("Experiment sent !")

