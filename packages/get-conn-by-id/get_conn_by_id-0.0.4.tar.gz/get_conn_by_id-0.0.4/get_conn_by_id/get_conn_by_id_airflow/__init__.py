
import inspect
from airflow.hooks.base_hook import BaseHook
import json

def get_conn_by_id_airflow(conn_id):

    cred_conn = BaseHook.get_connection(conn_id)

    cred_dict = {}
    for attribute in dir(cred_conn):
        print(cred_conn, 'attr: ', attribute)

        if not attribute.startswith('__'):
            if not inspect.ismethod(attribute):
                cred_dict[attribute] = getattr(cred_conn, attribute)
                if attribute == 'schema':
                    cred_dict['database'] = getattr(cred_conn, attribute)
                elif attribute == 'login':
                    cred_dict['username'] = getattr(cred_conn, attribute)
                    cred_dict['client_id'] = getattr(cred_conn, attribute)
        
    cred_dict['password'] = cred_conn.get_password()
    cred_dict['token'] = cred_conn.get_password()
    cred_dict['api_key'] = cred_conn.get_password()
    cred_dict['secret'] = cred_conn.get_password()

    cred_extra = cred_conn.get_extra()

    if len(cred_extra) > 2:
        cred_extra_json = json.loads(cred_extra)

        cred_dict = {**cred_dict, **cred_extra_json}

    print('cred_dict: ', cred_dict)
    
    return cred_dict





    # server = email_conn.host
    # port = email_conn.port
    # send_from = json.loads(email_conn.get_extra())["send_from"]
    # username = email_conn.login
    # password = email_conn.get_password()