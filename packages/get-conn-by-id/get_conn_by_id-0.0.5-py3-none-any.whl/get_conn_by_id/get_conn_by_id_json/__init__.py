import json
from .get_credential_url import get_credential_url

def get_conn_by_id_json(conn_id, 
                        credential_url=None):
    
    if credential_url == None:
        credential_url = get_credential_url()

        if credential_url == None: # if there is no credential_url from localhost or databricks
            return None

    with open(credential_url) as f:
        credentials = json.load(f)


        
    for connection in credentials['connections']:
        if connection['connection_id'] == conn_id:
            return connection['secrets']
    
    print('[INFO]: cannot found the connection_id!')
    return None # if there is no such credential id yet

    # raise('cannot found the connection_id!')