import json
import logging
import os
import time
from contextlib import contextmanager
from datetime import datetime

import psycopg2
import psycopg2.extras
from backoff import backoff
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from psycopg2 import DatabaseError, Error, OperationalError
from queries import filmworks_query, genres_query, persons_query
from state_storage import JsonFileStorage, State

load_dotenv('.env')

FILMWORKS_INDEX = "movies"
GENRES_INDEX = "genres"
PERSONS_INDEX = "persons"
SLEEP_INTERVAL = 30  # Interval in seconds

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def postgres_connection(**connection_params):
    pg_conn = psycopg2.connect(
        **connection_params, cursor_factory=psycopg2.extras.DictCursor)
    try:
        yield pg_conn
    finally:
        pg_conn.close()


@backoff
def fetch_data_from_postgres(query, last_processed_timestamp):
    """Connect and Fetch data from PostgreSQL"""
    dsl = {
        'dbname': os.environ.get('POSTGRES_DB', 'films_database'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    with postgres_connection(**dsl) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, (last_processed_timestamp,))
            data = cursor.fetchall()
            cursor.close()
            return data
        except (OperationalError, DatabaseError, Error) as e:
            # Handle specific database errors
            logger.info(f"Database error occurred: {e}")
            raise


@backoff
def import_data_to_es(bulk_data, index):
    es = connect_to_elasticsearch()
    if bulk_data is None or bulk_data == '':
        return
    response = es.bulk(body=bulk_data, index=index)
    if response['errors']:
        raise ValueError(
            f"Error inserting data into Elasticsearch: {response}")
    else:
        logger.info("Data inserted successfully into Elasticsearch.")
    return response


def connect_to_elasticsearch():
    """Establishes connection to Elasticsearch."""
    scheme = os.environ.get('ELASTICSEARCH_SCHEME', 'http')
    host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
    port = os.environ.get('ELASTICSEARCH_PORT', '9200')

    es = Elasticsearch(hosts=[f'{scheme}://{host}:{port}'])
    return es


def prepare_filmworks(data):
    bulk_data = ''
    for item in data:
        index_meta = {"update": {"_id": item[0], "_index": FILMWORKS_INDEX}}
        document = {
            "id": item[0],
            "title": item[1],
            "description": item[2],
            "imdb_rating": item[3],
            "actors": [{"id": it['person_id'], "name": it['person_name']} for it in item[7] if it['person_role'] == 'actor'],
            "actors_names": [it['person_name'] for it in item[7] if it['person_role'] == 'actor'],
            "directors": [{"id": it['person_id'], "name": it['person_name']} for it in item[7] if it['person_role'] == 'director'],
            "directors_names": [it['person_name'] for it in item[7] if it['person_role'] == 'director'],
            "writers": [{"id": it['person_id'], "name": it['person_name']} for it in item[7] if it['person_role'] == 'writer'],
            "writers_names": [it['person_name'] for it in item[7] if it['person_role'] == 'writer'],
            "genres": [{"id": it['genre_id'], "name": it['genre_name']} for it in item[8]],
        }
        upsert_script = {
            "scripted_upsert": True,
            "script": {
                "source": "ctx._source.id = params.id; ctx._source.title = params.title; ctx._source.description = params.description; ctx._source.imdb_rating = params.imdb_rating; ctx._source.actors = params.actors; ctx._source.actors_names = params.actors_names; ctx._source.directors = params.directors; ctx._source.directors_names = params.directors_names; ctx._source.writers = params.writers; ctx._source.writers_names = params.writers_names; ctx._source.genres = params.genres;",
                "params": document
            },
            "upsert": document
        }
        bulk_data += json.dumps(index_meta) + '\n' + \
            json.dumps(upsert_script) + '\n'
    return bulk_data


def prepare_genres(data):
    bulk_data = ''
    for item in data:
        index_meta = {"update": {"_id": item[0], "_index": GENRES_INDEX}}
        document = {
            "id": item[0],
            "genre": item[1]
        }
        upsert_script = {
            "scripted_upsert": True,
            "script": {
                "source": "ctx._source.id = params.id; ctx._source.genre = params.genre;",
                "params": document
            },
            "upsert": document
        }
        bulk_data += json.dumps(index_meta) + '\n' + \
            json.dumps(upsert_script) + '\n'
    return bulk_data


def prepare_persons(data):
    bulk_data = ''
    for item in data:
        index_meta = {"update": {"_id": item[0], "_index": PERSONS_INDEX}}
        document = {
            "id": item[0],
            "person": item[1],
            "films": [{
                "id": film['id'],
                "imdb_rating": film['imdb_rating'],
                "title": film['title'],
                "role": film['role']}
                for film in item[2]]
        }
        upsert_script = {
            "scripted_upsert": True,
            "script": {
                "source": "ctx._source.id = params.id; ctx._source.person = params.person; ctx._source.films = params.films;",
                "params": document
            },
            "upsert": document
        }
        bulk_data += json.dumps(index_meta) + '\n' + \
            json.dumps(upsert_script) + '\n'
    return bulk_data


def transfer_filmworks(storage):
    last_processed_timestamp_filmworks = storage.get_state(
        'last_processed_timestamp_filmworks')
    logger.info(
        f"Update ES {FILMWORKS_INDEX} with new content from: {last_processed_timestamp_filmworks}")
    data = fetch_data_from_postgres(
        filmworks_query, last_processed_timestamp_filmworks)
    bulk_data = prepare_filmworks(data)
    import_data_to_es(bulk_data, FILMWORKS_INDEX)
    storage.set_state('last_processed_timestamp_filmworks',
                      datetime.now().isoformat())


def transfer_genres(storage):
    last_processed_timestamp_genres = storage.get_state(
        'last_processed_timestamp_genres')
    logger.info(
        f"Update ES {GENRES_INDEX} with new content from: {last_processed_timestamp_genres}")
    data = fetch_data_from_postgres(
        genres_query, last_processed_timestamp_genres)
    bulk_data = prepare_genres(data)
    import_data_to_es(bulk_data, GENRES_INDEX)
    storage.set_state('last_processed_timestamp_genres',
                      datetime.now().isoformat())


def transfer_persons(storage):
    last_processed_timestamp_persons = storage.get_state(
        'last_processed_timestamp_persons')
    logger.info(
        f"Update ES {PERSONS_INDEX} with new content from: {last_processed_timestamp_persons}")
    data = fetch_data_from_postgres(
        persons_query, last_processed_timestamp_persons)
    bulk_data = prepare_persons(data)
    import_data_to_es(bulk_data, PERSONS_INDEX)
    storage.set_state('last_processed_timestamp_persons',
                      datetime.now().isoformat())


def main(storage):
    transfer_filmworks(storage)
    transfer_genres(storage)
    transfer_persons(storage)


if __name__ == "__main__":
    storage_path = JsonFileStorage('es_state.json')
    storage = State(storage_path)
    logger.info("Starting ETL scheduler...")
    while True:
        main(storage)
        logger.info(f"\nSleeping for {SLEEP_INTERVAL} seconds.")
        time.sleep(SLEEP_INTERVAL)
