"""CLI to manipulate the database directly."""

import logging

import pymongo
from pymongo import ASCENDING, IndexModel
import typer

from app.console import console
from app.ops.database_user import app as database_user_app

logger = logging.getLogger(__name__)

app = typer.Typer()
app.add_typer(database_user_app, name='user')

BLEND_COLLECTION_NAME = 'blends'
SEQUIN_COLLECTION_NAME = 'sequins'
VARIANT_COLLECTION_NAME = 'variants'
GROUP_COLLECTION_NAME = 'groups'
LOCATION_COLLECTION_NAME = 'locations'
PART_DEFINITIONS_COLLECTION_NAME = 'part_definitions'
PART_COLLECTION_NAME = 'parts'
TILE_COLLECTION_NAME = 'tiles'
POOL_COLLECTION_NAME = 'pools'
USER_COLLECTION_NAME = 'users'

INDEXES = {
    SEQUIN_COLLECTION_NAME: [
        {'keys': [('id', ASCENDING)], 'unique': True},
        {'keys': [('sequence', ASCENDING)], 'unique': True},
    ],
    VARIANT_COLLECTION_NAME: [
        {
            'keys': [
                ('chrom', ASCENDING),
                ('pos', ASCENDING),
                ('ref', ASCENDING),
                ('alt', ASCENDING),
            ],
            'unique': True,
        }
    ],
    GROUP_COLLECTION_NAME: [
        {'keys': [('id', ASCENDING)], 'unique': True},
        {'keys': [('sequin_ids_hash', ASCENDING)], 'unique': True},
    ],
    BLEND_COLLECTION_NAME: [{'keys': [('id', ASCENDING)], 'unique': True}],
    PART_DEFINITIONS_COLLECTION_NAME: [
        {
            'keys': [('part_number', ASCENDING)],
            'unique': True,
        },
    ],
    PART_COLLECTION_NAME: [
        {
            'keys': [('part_number', ASCENDING)],
            'unique': True,
        },
        {
            'keys': [
                ('part_number', ASCENDING),
                ('constituent_lots_hash', ASCENDING),
            ],
            'unique': True,
        },
        {'keys': [('location', ASCENDING)], 'unique': False},
        {'keys': [('status', ASCENDING)], 'unique': False},
        {
            'keys': [('status', ASCENDING), ('quote_reference', ASCENDING)],
            'unique': False,
        },
        {'keys': [('created_at_utc', ASCENDING)], 'unique': False},
    ],
    TILE_COLLECTION_NAME: [
        {'keys': [('id', ASCENDING)], 'unique': True},
        {'keys': [('sequence', ASCENDING)], 'unique': False},
    ],
    POOL_COLLECTION_NAME: [{'keys': [('id', ASCENDING)], 'unique': True}],
    USER_COLLECTION_NAME: [
        {'keys': [('username', ASCENDING)], 'unique': True},
        {'keys': [('api_key_hash', ASCENDING)], 'unique': False},
    ],
    LOCATION_COLLECTION_NAME: [
        {'keys': [('name', ASCENDING)], 'unique': False},
        {'keys': [('parent_key', ASCENDING)], 'unique': False},
    ],
}


@app.command(name='create-indexes')
def create_indexes(ctx: typer.Context):
    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    logger.debug('server = %s, database = %s', server, database)

    console.log(f'Creating indexes for database {database}.')

    client = pymongo.MongoClient(server)
    db = client[database]

    for collection_name, indexes in INDEXES.items():
        index_models = [
            # pyrefly: ignore  # bad-argument-type
            IndexModel(index['keys'], unique=index['unique'])
            for index in indexes
        ]
        db[collection_name].create_indexes(index_models)

    console.log('Indexes created successfully.')


@app.command(name='sync-indexes')
def sync_indexes(ctx: typer.Context):
    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    logger.debug('server = %s, database = %s', server, database)

    console.log(f'Syncing indexes for database {database}.')

    client = pymongo.MongoClient(server)
    db = client[database]

    # Create existing indexes if they do not already exist.
    for collection_name, indexes in INDEXES.items():
        existing_indexes = db[collection_name].list_indexes()
        existing_index_names = {index['name'] for index in existing_indexes}

        index_models = []
        for index in indexes:
            # pyrefly: ignore  # bad-argument-type
            index_model = IndexModel(index['keys'], unique=index['unique'])
            if index_model.document['name'] not in existing_index_names:
                index_models.append(index_model)

        if index_models:
            db[collection_name].create_indexes(index_models)

    # Drop indexes that are not in our defined set.
    for collection_name, indexes in INDEXES.items():
        defined_index_names = {
            # pyrefly: ignore  # bad-argument-type
            IndexModel(index['keys'], unique=index['unique']).document['name']
            for index in indexes
        }

        existing_indexes = db[collection_name].list_indexes()
        extra_indexes = []
        # pyrefly: ignore  # bad-assignment
        for index in existing_indexes:
            if (
                index['name'] not in defined_index_names
                and index['name'] != '_id_'
            ):
                extra_indexes.append(index['name'])

        if extra_indexes:
            for index_name in extra_indexes:
                db[collection_name].drop_index(index_name)

    console.log('Indexes synced successfully.')


@app.command(name='drop')
def drop_database(ctx: typer.Context):
    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    logger.debug('server = %s, database = %s', server, database)

    client = pymongo.MongoClient(server)
    client.drop_database(database)

    console.log('Database dropped successfully.')
