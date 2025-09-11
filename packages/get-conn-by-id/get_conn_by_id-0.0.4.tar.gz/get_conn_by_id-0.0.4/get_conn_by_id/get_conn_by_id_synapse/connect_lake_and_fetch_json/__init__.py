
from azure.storage.filedatalake import DataLakeServiceClient
import io
import json


def connect_lake_and_fetch_json(datalake, account_key):

    # connect to the datalake and fetch the json file
    azure_service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", datalake.account_name), credential=account_key)
        
    azure_file_system_client = azure_service_client.get_file_system_client(file_system=datalake.container_name)

    file_client = azure_file_system_client.get_file_client(datalake.file_path)
    data = file_client.download_file().readall()
    json_dict = json.load(io.BytesIO(data))

    return json_dict