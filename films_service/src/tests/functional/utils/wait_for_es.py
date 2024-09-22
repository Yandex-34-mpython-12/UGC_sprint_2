from src.tests.functional.settings import test_settings
from elasticsearch import Elasticsearch
from backoff import backoff
import sys
import os

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Step up two levels to the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir, os.pardir))

# Add the parent directory to the system path
sys.path.insert(0, parent_dir)

# Now you can import the module


# Define a function to attempt connecting to Elasticsearch
def connect_to_elasticsearch():
    es_client = Elasticsearch(
        hosts=f'{test_settings.elastic_schema}://{test_settings.elastic_host}:{test_settings.elastic_port}',
        verify_certs=False,
    )
    if es_client.ping():
        print('Connected to Elasticsearch successfully!')
        return es_client
    else:
        print('Failed to connect to Elasticsearch.')
        raise ConnectionError('Elasticsearch ping failed.')


# Use backoff to handle retries
@backoff
def main():
    es_client = connect_to_elasticsearch()
    return es_client


if __name__ == '__main__':
    es_client = main()
