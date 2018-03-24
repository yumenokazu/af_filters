import logging
import typing

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from config import basedir
from string import ascii_uppercase as letters

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sheets API' # OAuth client ID app name


def _get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(basedir, 'filter_app', 'gsheets')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def _setup_conn():
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl, cache_discovery=False)
    return service


def get_sheet_data(spreadsheet_id: str, range_name: str):
    """ Gets data within range from spreadsheet.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit

    :param spreadsheet_id: identifies which spreadsheet is to be accessed or altered, as in URL
    :param range_name: [sheet id]![A1 notation range], e.g List1!A1:E4
    """
    service = _setup_conn()

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', []) # get dictionary value for key 'values', [] if not found

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(",".join([x for x in row]))


def get_row_cells(spreadsheet_id: str, list_name: str, row_num: int):
    """ Gets data within range from spreadsheet.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit

    :param spreadsheet_id: identifies which spreadsheet is to be accessed or altered, as in URL
    :param list_name: name of the list
    :param row_num: number of row to be searched
    """
    service = _setup_conn()

    range_name = "%s!%s:%s" % (list_name, row_num, row_num)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', []) # get dictionary value for key 'values', [] if not found
    return values


def write_sheet_data(spreadsheet_id: str, range_name: str, values: typing.List, major_dim:str = None):
    """ Writes values to the spreadsheet

    :param spreadsheet_id: identifies which spreadsheet is to be accessed or altered, as in URL
    :param range_name: [sheet id]![A1 notation range], e.g List1!A1:E4
    :param values: list of values to insert
    :param major_dim: major dimension option of body object: 'ROW" or 'COLUMN'
    """
    service = _setup_conn()

    if major_dim is None:
        major_dim = "ROWS"
    else:
        major_dim = "COLUMNS"
    body = {'majorDimension': major_dim, 'values': values}
    value_input_option = 'RAW' # RAW or USER_ENTERED

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()


def append_sheet_data(spreadsheet_id: str, range_name: str, values: typing.List, major_dim:str = None):
    """ Appends values to the spreadsheet

    Google Documentation: https://developers.google.com/sheets/api/guides/values#appending_values

    :param spreadsheet_id: identifies which spreadsheet is to be accessed or altered, as in URL
    :param range_name: [sheet id]![A1 notation range], e.g List1!A1:E4
    :param values: list of values to insert
    :param major_dim: major dimension option of body object: 'ROW" or 'COLUMN'
    """

    service = _setup_conn()

    if major_dim is None:
        major_dim = "ROWS"
    else:
        major_dim = "COLUMNS"
    body = {'majorDimension': major_dim, 'values': values}
    value_input_option = 'RAW' # RAW or USER_ENTERED

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()


def _convert_num_to_colname(num: int) -> str:
    """
    Converts positive integer into string representing corresponding column in A1 notation without sheet name
    A1 notation: https://developers.google.com/sheets/api/guides/concepts#a1_notation

    :param num: number to be converted
    :return: name of the column in A1 notation, e.g. 'AAB'
    """
    if num > 0:
        num_of_letters = len(letters)
        DIVMOD = divmod(num, num_of_letters)
        if DIVMOD[0] == 0:
            return letters[DIVMOD[1]-1]
        elif DIVMOD[1] == 0:
            return letters[DIVMOD[0]-1]
        else:
            return _convert_num_to_colname(DIVMOD[0])+letters[DIVMOD[1]-1]
    else:
        raise ValueError("given num parameter (%s) is not positive" % num)


if __name__ == "__main__":
    spreadsheet_id = '1Z1A03eGihrpevvZtNvcCGfKpqyQMxqB8pAPj8gp81Ic'
    cells = get_row_cells(spreadsheet_id, 'uarmours', 1)
    if len(cells) > 0:
        cells = cells[0]
        print(_convert_num_to_colname(len(cells)))