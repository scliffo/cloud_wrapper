"""
Primary wrapper analysis code
"""
import json
import importlib
from pathlib import Path
from jsonmerge import merge

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
    analytics_config = json.load(open('config/default.json'))
    if config is not None:
        analytics_config = merge(analytics_config, config)

    # from process.analytics import process
    if 'analytics' in analytics_config:
        print('Using analytics module:', analytics_config['analytics'])
        analytics = importlib.import_module(analytics_config['analytics'])
    else:
        analytics = importlib.import_module('process.analytics')

    data_store = storage.DataStore(analytics_config, data)
    data_store.store(device, analytics.process(data_store.retrieve(device)))
