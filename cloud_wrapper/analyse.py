"""
Primary wrapper analysis code
"""
import json
import importlib
from jsonmerge import merge
import os
from linetimer import CodeTimer

if __package__ == '':
    import storage
else:
    from . import storage

def _load_config(config_path):
    if config_path.endswith('.json'):
        return json.load(open(config_path))
    else:
        return importlib.import_module(config_path).config

def analyse(device, config=None, data=None):
    """
    Data sample posted to AWS by device
    Load data from storage using device ID
    Call analytics module passing data in a Python object
    Analytics runs and updates data objects as necessary
    Updates are persisted to storage medium
    """
    with CodeTimer('analyse'):
        _run_analysis(device, config=config, data=data)

def _run_analysis(device, config=None, data=None):
    # If CW_CONFIG is set use it to find configuration
    # Otherwise look for config/default.json or config/configure.py in that order
    if 'CW_CONFIG' in os.environ:
        config_path = os.environ['CW_CONFIG']
        analytics_config = _load_config(config_path)
    else:
        config_path = 'config/default.json'
        if os.path.exists(config_path):
            analytics_config = _load_config(config_path)
        else:
            analytics_config = _load_config('config.configure')
    print('Loaded configuration from', config_path)
    
    # If supplementary config information is provided merge it
    if config is not None:
        analytics_config = merge(analytics_config, config)
    
    # Find the analytics module and import it
    if 'analytics' in analytics_config:
        print('Using analytics module:', analytics_config['analytics'])
        analytics = importlib.import_module(analytics_config['analytics'])
    else:
        analytics = importlib.import_module('process.analytics')

    data_store = storage.DataStore(analytics_config, data)
    with CodeTimer('retrieve data'):
        device_data = data_store.retrieve(device)
    with CodeTimer('process data'):
        result = analytics.process(device_data)
    with CodeTimer('store data'):
        data_store.store(device, result)

