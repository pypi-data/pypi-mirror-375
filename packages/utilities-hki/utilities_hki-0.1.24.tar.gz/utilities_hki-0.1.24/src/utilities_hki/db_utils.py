"""
Database utility functions.
Copyright (C) 2022 Humankind Investments
"""

import psycopg2
from psycopg2.extras import execute_batch
from psycopg2 import sql

import pandas as pd


def get_data(db_name, db_cred, query):
    """
    Get data from database for given query.

    Parameters
    ----------
    db_name : str
        Name of database on instance.
    db_cred : dict
        Dictionary of database instance credentials, where keys are 
        'endpoint', 'port', 'username', and 'pw'.
    query : str
        Query with which to read data from database.

    Returns
    -------
    pd.DataFrame
        Dataframe of data based on query.
    """

    cursor, conn = database_connect(db_name, db_cred)
    df = pd.read_sql(query, conn)
    cursor.close()
    conn.close()

    return df


def database_connect(db_name, db_cred):
    """
    Connect to database with given name and instance credentials.

    Parameters
    ----------
    db_name : str
        Name of database on instance.
    db_cred : dict
        Dictionary of credentials for database instance, where keys are 
        'endpoint', 'port', 'user', and 'pw', e.g.:
            db_cred = {'endpoint' : [instance-endpoint],
                       'port' : [connection-port-number],
                       'user' : [username],
                       'pw' : [password]}.

    Returns
    -------
    psycopg2.connection.cursor
        Database connection cursor object.
    psycopg2.connection
        Database connection object.
    """

    conn = psycopg2.connect(host = db_cred['endpoint'],
                            port = db_cred['port'],
                            database = db_name,
                            user = db_cred['username'],
                            password = db_cred['pw'],
                            )

    return conn.cursor(), conn


def database_write(df, db_name, db_cred, table_query, table_name):
    """
    Write data to table in database.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to insert into table in database.
    db_name : str
        Name of database on instance.
    db_cred : dict
        Dictionary of database instance credentials, where keys are 
        'endpoint', 'port', 'username', and 'pw'.
    table_query : str
        Initial table creation query.
    table_name : str
        Name of table in which to insert data.
    """

    # connect to database
    cursor, conn = database_connect(db_name, db_cred)

    # create initial table
    cursor.execute(table_query)
    conn.commit()

    # write data to table in DB
    tdict = df.to_dict(orient='records')
    query = insert_data(table_name, df.columns)
    execute_batch(cursor, query, tdict)
    conn.commit()

    cursor.close()
    conn.close()

    
def insert_data(table, columns):
    """
    Create insert query.

    Parameters
    ----------
    table : str
        Name of table in which to insert data.
    columns : list of str
        List of column names in table.
    
    Returns
    -------
    insert : sql query
        SQL insert query.
    """

    insert = sql.SQL('INSERT INTO {} ({}) VALUES({});').format(
        sql.Identifier(table),
        sql.SQL(',').join(map(sql.Identifier, columns)),
        sql.SQL(',').join(map(sql.Placeholder, columns))
        )

    return insert


def connect_dynamo_table(session, table_name):
    """
    Connect to DynamoDB table.

    Parameters
    ----------
    session : boto3.session.Session
        Boto3 session object.
    table_name : str
        Name of table.
    
    Returns
    -------
    DynamoDB.Table
        DynamoDB table resource.
    """
    
    # connect to dynamodb table
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)

    return table
