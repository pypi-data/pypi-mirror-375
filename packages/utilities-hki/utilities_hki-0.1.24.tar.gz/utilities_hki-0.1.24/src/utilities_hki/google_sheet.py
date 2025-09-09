"""
Read google sheets with retries.
Copyright (C) 2022 Humankind Investments
"""

import time, os 
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Timeout between retries in seconds
BACKOFF_FACTOR = 5
# Maximum number of retries for errors
MAX_RETRIES = 5


def get_client(cred_path):
    """
    Get a gspread client using service account credentials.

    Parameters
    ----------
    cred_path : str
        Path to the directory containing the client_secrets.json file.
    """

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(cred_path, 'client_secrets.json'), scope)
    client = gspread.authorize(creds)
    return client


def read_sheet(filename, client=None, cred_path=None, clear_flag=False):
    """
    Read a Google Sheets file and extract a DataFrame.

    Parameters
    ----------
    filename : str
        Name of the Google Sheets file.
    client : gspread.Client, optional
        Gspread client to use. If None, a new client is created.
    cred_path : str, optional
        Path to the directory containing the client_secrets.json file.
    clear_flag : bool, optional
        If True, the Google Sheets file is cleared after reading. 
        Default is False.

    Returns
    -------
    pandas.DataFrame
        Dataframe of the Google Sheets file.
    gspread.Spreadsheet
        Object to continue interacting with the Google Sheet.
    """
    if (client is None) and (cred_path is None):
        raise ValueError("Either client or cred_path must be provided.")
    elif client is None:
        client = get_client(cred_path)

    retry_count = 0
    # retry until successful or max retries reached
    while True:
        try:
            sheet = client.open(filename).sheet1
            data = sheet.get_all_records()
            break
        except gspread.exceptions.APIError as e:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                time.sleep(BACKOFF_FACTOR * (2 ** retry_count))
            else:
                raise e
    df = pd.DataFrame.from_records(data)

    if clear_flag: sheet.clear()

    return df, sheet


def write_sheet(df, filename, client=None, cred_path=None):
    """
    Write a DataFrame to a Google Sheets file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to write to the Google Sheets file.
    filename : str
        Name of the Google Sheets file.
    client : gspread.Client, optional
        Gspread client to use. If None, a new client is created.
    cred_path : str, optional
        Path to the directory containing the client_secrets.json file.

    Returns
    -------
    gspread.Spreadsheet
        Object to continue interacting with the Google Sheet.
    """
    if (client is None) and (cred_path is None):
        raise ValueError("Either client or cred_path must be provided.")
    elif client is None:
        client = get_client(cred_path)

    # retry until successful or max retries reached
    retry_count = 0
    # retry until successful or max retries reached
    while True:
        try:
            sheet = client.open(filename).sheet1
            sheet.clear()
            # Nans are not allowed in json.dumps()
            sheet.update([df.columns.values.tolist()] + df.fillna('').values.tolist())
            break
        except gspread.exceptions.APIError as e:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                time.sleep(BACKOFF_FACTOR * (2 ** retry_count))
            else:
                raise e
    
    return sheet
