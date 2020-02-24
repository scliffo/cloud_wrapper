
# Cloud Wrapper for Analytics

A simple wrapper for running analytics code locally and also in an AWS Lambda or Docker container.

The wrapper abstracts the process of retrieving and storing data allowing analytics code to be
expressed as a Python function that takes a map of inputs and returns a map of outputs.

    {inputs} -> process() -> {outputs}

Both the inputs and outputs are maps with key/value pairs where each value is a JSON string.

This provide a very simple interface for an analytics module, at the cost of some inefficiency
in marshalling data to JSON and parsing it on return. It also assumes that the quantity of data
is small enough so as to comfortably fit in memory.

## Installation

Installation is simple, just use pip like so

    pip install cloud_wrapper

## Configuration

Configuration is set in a file called `config/default.json` in the project folder.
A typical configuration file looks like this

    {
        "analytics": "analytics.analytics",
        "storage": {
            "defaults": {
                "path": "local/db"
            },
            "inputs": [
                "sample",
                "model"
            ],
            "outputs": [
                "model"        ],
            "partitions": {
                "model": {
                    "model": "SimpleFileDataStore"
                },
                "sample": {
                    "model": "InputDataStore"
                }
            }
        }
    }

This defines two inputs and out output. All data is stored locally in `local/db`. Sample data is passed
via an input file and model data is stored in a simple JSON file.

## Running

Once installed and configured running analytics is simple

    python -m cloud_wrapper (device-id) (sample-file.json)
