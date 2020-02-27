"""
Primary wrapper analysis code
"""
import json
import importlib
from jsonmerge import merge
import os

if __package__ == '':
    import storage
else:
    from . import storage

def analyse(device, config=None, data=None):
    """
    Data sample posted to AWS by device
    Load data from storage using device ID
    Call analytics module passing data in a Python object
    Analytics runs and updates data objects as necessary
    Updates are persisted to storage medium
    """
    config_path = 'config/default.json'
    if os.path.exists(config_path):
        analytics_config = json.load(open(config_path))
    else:
        config_path = 'config/configure.py'
        analytics_config = importlib.import_module('config.configure').config
    
    if config is not None:
        analytics_config = merge(analytics_config, config)
    
    if 'analytics' in analytics_config:
        print('Using analytics module:', analytics_config['analytics'])
        analytics = importlib.import_module(analytics_config['analytics'])
    else:
        analytics = importlib.import_module('process.analytics')

    data_store = storage.DataStore(config, data)
    data_store.store(device, analytics.process(data_store.retrieve(device)))
