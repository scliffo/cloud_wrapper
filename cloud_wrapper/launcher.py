
"""
Main Cloud Wrapper command line launcher
"""
from cloud_wrapper.analyse import analyse
import json

# Call analytics method
def launch(argv):
    if len(argv) > 2:
        print('Loading sample data from ', argv[2])
        analyse(argv[1], data={ 'sample': open(argv[2]).read() })
    elif len(argv) > 1:
        print('Loading data from local data store', argv[1])
        analyse(argv[1])
    else:
        print('usage: process.py <device-id> [optional-sample-data-file]')
