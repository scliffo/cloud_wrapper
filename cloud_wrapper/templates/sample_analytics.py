"""
Sample analytics file
"""

import json

def process(data: dict) -> dict:
    """
    Function to run analytics process.
    Data is passed in as a map using the 'inputs' keys defined in config/default.json
    """
    print('Welcome to Sample Analytics', len(data))

    # To access the raw JSON string for a key
    motor = data['motor']
    print('motor:', motor)

    # It may be useful to parse data using the json package
    sample = json.loads(data['sample'])
    print('sample:', sample)

    # Iterate through the data as normal in python
    for key, value in data.items():
        print('data[' + key + '] found', len(value), 'bytes')


    # To store data pass it back out in a map using the 'outputs' keys defined in
    # config/default.json
    # If you have no data to return for a key then do not include the key in the map
    # To return nothing at all simply return an empty map like so 'return {}'
    return {
        # For simple JSON objects its possible to perform an update.
        # This is how to update the 'motor.ml' block of a JSON object.
        # Parts of object outside of the 'ml block' are unchanged.
        "motor.ml": json.dumps({
            "learning": 1,
            "modelGenerated": 0
        }),
        # Its also possible to replace an entire object.
        # In this case 'model' is overwritten with whatever we pass out.
        "model": json.dumps({
            "my_int": 1,
            "my_float": -0.123,
            "my_string": "hello"
        }),
        # For collections of objects which can be appended to just return
        # any new records you want to add
        "critfreq": json.dumps([
            {"entity1": {"data1": "value1"}},
            {"entity2": {"data2": "value2"}},
        ])
    }
