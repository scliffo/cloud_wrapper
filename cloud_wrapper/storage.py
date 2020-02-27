"""
Data storage layer
"""
from pathlib import Path
import json
import boto3
from boto3.dynamodb.conditions import Attr
import botocore
from jsonmerge import merge
import decimal
import uuid
import time

class DataStoreException(Exception):
    """
    Exception class
    """
    pass
class DataStore:
    """
    Store for data organised by partitions. Partitions can be stored in different locations and systems.
    """
    def __init__(self, config, data=None):
        self.config = config
        self.data = data
        self.partitions = config['storage']['partitions']
        self.readable = config['storage']['inputs']
        self.writable = config['storage']['outputs']

    def retrieve(self, key):
        """
        Get all data for a specific key (e.g. a device id).
        The data is returned in a list, with a JSON string per readable partition.
        """
        result = {}

        for partition in self.readable:
            try:
                params = self._merge_params(key, partition)
                if self.data:
                    params['data'] = self.data
                if partition in self.partitions:
                    store = self.partitions[partition]["model"].split(",")
                    ds = eval(store[0] + "(params)")
                else:
                    ds = SimpleFileDataStore(params)
                result[partition] = ds.get()
            except Exception as err:
                print("ERROR:", partition, "- unable to load " + partition + " data for " + key)
                print("ERROR:", partition, "-", repr(err))
                result[partition] = None

        return result

    def store(self, key, values):
        """
        Store updated data for a specific key (e.g. a device id).
        Only data for writable partitions will be stored or updated.
        """
        if values is None:
            raise DataStoreException("No value passed to data store. Did your analytics function return a value?.")

        for partition in values:
            try:
                if partition in self.writable:
                    if "." in partition:
                        words = partition.split(".")
                        partition = words[0]
                        attr = words[1:]
                    else:
                        attr = None

                    if partition in self.partitions:
                        params = self._merge_params(key, partition)
                        store = self.partitions[partition]['model'].split(",")
                        ds = eval(store[len(store)-1] + '(params)')
                        if attr is None:
                            ds.put(values[partition])
                        else:
                            ds.update(attr, values[partition + "." + ".".join(attr)])
                else:
                    print("storing " + partition + " data not supported")
            except Exception as err:
                print("ERROR:", partition, "- unable to store " + partition + " data for " + key)
                print("ERROR:", partition, "-", repr(err))

    def _merge_params(self, key, partition):
        params = merge(self.partitions[partition], self.config["storage"]["defaults"])
        if "key" in params:
            params = merge(params, { "partition": partition })
        else:
            params = merge(params, { "partition": partition, "key": key })

        for index, value in params.items():
            if value.startswith('eval:'):
                params[index] = self._eval(key, partition, value[5:])

        return params

    def _eval(self, key, partition, expression):
        """
        Evaluate an expression. This has its own method to provide an isolated
        context with only self, key, partition and expression as possible attributes.
        """
        try:
            return eval(expression)
        except Exception as err:
            print("ERROR:", partition, "- unable to evaluate expression ", expression)
            print("ERROR:", partition, "key:", key, " partition:", partition)
            print("ERROR:", partition, "-", repr(err))


class _UpdatableDataStore:
    """
    Data store containing a JSON object than can be updated
    """
    def get(self) -> str:
        return self.read()

    def put(self, value):
        self.write(value)

    def update(self, attr, value):
        return self.put(self.update_json(self.get(), attr, value))

    def update_json(self, json_str: str, attr: list, value: str):
        data = json.loads(json_str)
        last = attr[-1]
        item = data
        for a in attr[:-1]:
            if a not in item:
                item[a] = {}
            item = item[a]
        item[last] = json.loads(value)
        return json.dumps(data, indent=4)

class _FileDataStore:
    """
    Data store using a local file
    """
    def read(self) -> str:
        f = None
        try:
            f = open(self.path)
            return f.read().strip()
        finally:
            if f is not None:
                f.close()

    def write(self, value):
        f = None
        try:
            f = open(self.path, "w")
            return f.write(value)
        finally:
            if f is not None:
                f.close()

    def exists(self) -> bool:
        return self.path.is_file()

class _S3DataStore:
    """
    Data store using an S3 bucket
    """
    def read(self) -> str:
        s3_obj = self._s3().get_object(Bucket=self.bucketname, Key=self.path)
        return s3_obj['Body'].read().decode('utf-8').strip()

    def write(self, value):
        self._s3().put_object(Bucket=self.bucketname, Key=self.path, Body=value)

    def exists(self) -> bool:
        try:
            response = self._s3().head_object(Bucket=self.bucketname, Key=self.path)
            return True
        except botocore.exceptions.ClientError:
            return False

    def _s3(self):
        session = boto3.Session()
        return session.client("s3")

# Helper class to convert a DynamoDB item to JSON.
class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(_DecimalEncoder, self).default(o)

class _DynamoDataStore:
    """
    Data store using a Dynamo table
    """
    def read(self) -> str:
        result = self._table().get_item(Key=self.key)
        if 'Item' in result:
            return json.dumps(result['Item'], cls=_DecimalEncoder)
        else:
            return None

    def write(self, value):
        self._table().put_item(Item=merge(json.loads(value), self.key))

    def exists(self) -> bool:
        self._table()

    def _table(self):
        session = boto3.Session()
        dynamodb = session.resource("dynamodb")
        return dynamodb.Table(self.tablename)


class _AppendingDataStore:
    """
    Data store containing a collection of JSON objects
    """
    def get(self) -> str:
        result = self.read()
        if result.startswith("["):
            return result
        else:
            return "[" + result + "]"

    def put(self, value):
        current = []
        if self.exists():
            current = json.loads(self.get())

        data = json.loads(value)
        if isinstance(data, list):
            current.extend(data)
        else:
           current.append(data)

        self.write(json.dumps(current))


#
# Public classes below
#

class SimpleNoopDataStore:
    """
    Simple data store that returns nothing, stores nothing, i.e. a no-op store.
    """
    def __init__(self, params):
        self.key = params['key']
        self.partition = params['partition']

    def get(self) -> str:
        print('get:', self.key, self.partition)
        return '{}'

    def put(self, value):
        print('put:', self.key, self.partition, value)

    def update(self, attr, value):
        print('update:', self.key, self.partition, attr, value)

class AppendingNoopDataStore(SimpleNoopDataStore):
    """
    Appending data store that returns nothing, stores nothing, i.e. a no-op store.
    """
    def get(self) -> str:
        print('get:', self.key, self.partition)
        return '[]'

class InputDataStore:
    """
    Input data store allowing data to be passed directly to the analytics process
    from the calling function or lambda.
    """
    def __init__(self, params):
        self.partition = params['partition']
        if 'data' in params:
            self.data = params['data'][self.partition]
        else:
            self.data = '{}'

    def get(self) -> str:
        return self.data

    def put(self, value):
        pass

    def update(self, attr, value):
        pass

class KinesisStreamOutput:
    """
    Output data to a kinesis stream
    """
    def __init__(self, params):
        self.key = params['key']
        self.partition = params['partition']
        self.streamname = params['streamname']
        self.datatype = params['datatype']
        self.tenant = params['tenant']

    def get(self) -> str:
        return None

    def put(self, value):
        kinesis = boto3.client('kinesis')
        record = json.loads(value)
        record['dataType'] = self.datatype
        record['timestamp'] = int(time.time() * 1000)
        record['tenantId'] = self.tenant
        record['motorId'] = self.key
        kinesis.put_record(StreamName=self.streamname,
            Data=str.encode(json.dumps(record).encode()),
            PartitionKey=str(uuid.uuid4()))

    def update(self, attr, value):
        pass

class SimpleFileDataStore(_UpdatableDataStore, _FileDataStore):
    """
    A very simple store where data is stored in single file as a single JSON blob.
    Supports updating of JSON attributes.
    """
    def __init__(self, params):
        self.path = Path(params['path']) / params['key'] / (params['partition'] + ".json")


class SimpleS3DataStore(_UpdatableDataStore, _S3DataStore):
    """
    A very simple store where data is stored in single S3 object as a single JSON blob.
    Supports updating of JSON attributes.
    """
    def __init__(self, params):
        self.bucketname = params['bucket']
        self.path = params['path'] + "/" + params['key'] + "/" + (params['partition'] + ".json")


class SimpleDynamoDataStore(_UpdatableDataStore, _DynamoDataStore):
    """
    A very simple store where data is stored in single S3 object as a single JSON blob.
    Supports updating of JSON attributes.
    """
    def __init__(self, params):
        self.tablename = params['table']
        self.key = params['key']

    def update(self, attr, value):
        if len(attr) > 1:
            item = attr[-1]
            update_expr = 'set ' + '.'.join(attr[:-1]) + '.' + item + ' = :' + item
        else:
            item = attr[0]
            update_expr = 'set ' + item + ' = :' + item
        attr_values = {':' + item : json.loads(value)}

        self._table().update_item(Key=self.key,
            UpdateExpression=update_expr,
            ExpressionAttributeValues=attr_values,
            ConditionExpression='attribute_exists(pk)'
        )

class DynamoCollectionDataStore(_DynamoDataStore):
    """
    Input data store extracting a collection of data from Dynamo.
    """
    def __init__(self, params):
        self.tablename = params['table']
        self.key = params['key']
        self.params = params

    def get(self) -> str:
        kwargs = {}
        args = ['KeyConditionExpression', 'ExpressionAttributeValues', 'ExpressionAttributeNames', 'IndexName']
        for arg in args:
            if arg in self.params:
                kwargs[arg] = self.params[arg]
        
        return json.dumps(self._table().query(**kwargs)['Items'])

    def put(self, value):
        pass


class AppendingFileDataStore(_AppendingDataStore,_FileDataStore):
    """
    Data store containing a collection of JSON objects in a local file
    """
    def __init__(self, params):
        self.path = Path(params['path']) / params['key'] / (params['partition'] + ".json")

class AppendingS3DataStore(_AppendingDataStore,_S3DataStore):
    """
    Data store containing a collection of JSON objects in an S3 object
    """
    def __init__(self, params):
        self.bucketname = params['bucket']
        self.path = params['path'] + "/" + params['key'] + "/" + (params['partition'] + ".json")

