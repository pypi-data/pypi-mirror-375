import os
from dotenv import load_dotenv
import pyodbc, struct
from azure import identity

def get_azure_conn():
    load_dotenv()
    connection_string = os.environ.get("AZURE_SQL_CONNECTIONSTRING", None)

    if connection_string is None:
        raise Exception("Missing ENV Var: AZURE_SQL_CONNECTIONSTRING")

    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})

    return conn
