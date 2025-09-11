
from .get_conn_by_id_json import get_conn_by_id_json

def get_conn_by_id(conn_id, 
                   account_key=None,
                   credential_url=None):
    
    # # fetching creds from local filesystem or datalake
    # cred_conn = get_conn_by_id_json(conn_id, 
    #                                 credential_url=credential_url)
    
    # if cred_conn != None:
    #     return cred_conn
    # else:
    #     # fetching creds from the airflow environment
    #     from .get_conn_by_id_airflow import get_conn_by_id_airflow
        
    #     cred_conn = get_conn_by_id_airflow(conn_id)

    # for testing
    cred_conn = None
    
    if cred_conn != None:
        return cred_conn
    else:
        # fetching creds from the synapse environment
        from .get_conn_by_id_synapse import get_conn_by_id_synapse

        if account_key is None:
            try:
                from notebookutils import mssparkutils
                account_key = mssparkutils.credentials.getConnectionStringOrCreds('AzureDataLakeStorageTest')
            except:
                raise Exception('Cannot get a valid account_key from mssparkutils, please provide one for getting credentials in the synapse environment')

        cred_conn = get_conn_by_id_synapse(conn_id, account_key)
        return cred_conn





