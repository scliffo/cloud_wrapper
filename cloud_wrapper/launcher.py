
"""
Main Cloud Wrapper command line launcher
"""
from cloud_wrapper.analyse import analyse
import json
import os

# Call analytics method
def launch(argv):
    if len(argv) > 2:
        path = argv[2]
        if os.path.isdir(path):
            for (folder, foldernames, filenames) in os.walk(path):
                for filename in filenames:
                    filepath = folder + '/' + filename
                    with open(filepath) as file:
                        print('Loading sample data from', filepath)
                        analyse(argv[1], data={ 'sample': file.read() })
        else:
            with open(path) as file:
                print('Loading sample data from', path)
                analyse(argv[1], data={ 'sample': file.read() })
    elif len(argv) > 1:
        print('Loading data from local data store', argv[1])
        analyse(argv[1])
    else:
        print('usage: process.py <device-id> [optional-sample-data-file] | [optional-sample-data-folder]')
