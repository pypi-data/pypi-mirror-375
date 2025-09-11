from . import datalake
from .connect_lake_and_fetch_json import connect_lake_and_fetch_json

def get_conn_by_id_synapse(conn_id, account_key):
    
    credentials = connect_lake_and_fetch_json(datalake, account_key)

    for connection in credentials['connections']:
        if connection['connection_id'] == conn_id:
            return connection['secrets']
    
    print('[INFO]: cannot found the connection_id!')
    return None # if there is no such credential id yet

    # raise('cannot found the connection_id!')