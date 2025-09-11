import os

from . import databricks
from . import local

def get_credential_url():

    for local_credential_url in local.credential_urls:
        if os.path.exists(local_credential_url):
            return local_credential_url
        
    for databricks_credential_url in databricks.credential_urls:
        if os.path.exists(databricks_credential_url):
            return databricks_credential_url
        
    print("[INFO]: Cannot find credentials from local server or databricks!")
    return None