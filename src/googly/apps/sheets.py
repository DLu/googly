import googly
import googleapiclient
import re

CELL_PATTERN = re.compile(r'^([A-Z]+)(\d+)$')
A_I = ord('A')

# Credit to
# https://github.com/jmcnamara/XlsxWriter/blob/main/xlsxwriter/utility.py


def coord_to_cell(col, row):
    assert row >= 0
    assert col >= 0
    letters = ''
    col += 1
    while col:
        rem = col % 26
        if rem == 0:
            rem = 26
        col = (col - 1) // 26
        letter = chr(A_I + rem - 1)
        letters = letter + letters
    return f'{letters}{row + 1}'


def cell_to_coord(spec):
    m = CELL_PATTERN.match(spec)
    col_s = m.group(1)
    row = int(m.group(2))
    col = 0
    for c in col_s:
        col *= 26
        c_i = ord(c)
        col += (c_i - A_I + 1)
    return col - 1, row - 1


class SheetsAPI(googly.API):
    # https://developers.google.com/sheets/api/guides/concepts

    class Scope(googly.Scope):
        SPREADSHEETS_READONLY = 1

    def __init__(self, spreadsheetId=None, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'sheets', 'v4', scopes, **kwargs)
        self.api = self.service.spreadsheets()
        self.set_sheet_id(spreadsheetId)
        self.metadata = {}

    def set_sheet_id(self, sheet_id):
        self.sheet_id = sheet_id

    def get_metadata(self):
        if self.sheet_id not in self.metadata:
            self.metadata[self.sheet_id] = self.api.get(spreadsheetId=self.sheet_id).execute()
        return self.metadata[self.sheet_id]

    def get_sheet_info(self, sheet):
        if sheet is None:
            sheet = 0
        meta = self.get_metadata()
        if isinstance(sheet, int):
            return meta['sheets'][sheet]
        elif isinstance(sheet, str):
            matching = [info for info in meta['sheets'] if info['properties']['title'] == sheet]
            if len(matching) == 1:
                return matching[0]
            else:
                names = [info['properties']['title'] for info in meta['sheets']]
                raise IndexError(f'Unable to find sheet named {sheet}. Valid names are {names}')
        else:
            raise IndexError(f'Cannot get sheet {sheet}')

    def get_size(self, sheet=None):
        sheet_info = self.get_sheet_info(sheet)
        gp = sheet_info['properties']['gridProperties']
        return gp['columnCount'], gp['rowCount']

    def get_values(self, range_spec):
        if self.sheet_id is None:
            raise Exception('Must specify spreadsheetId in constructor or by calling set_sheet_id')
        try:
            return self.api.values().get(spreadsheetId=self.sheet_id, range=range_spec).execute()
        except googleapiclient.errors.HttpError as e:
            if 'exceeds grid limits' in e.reason:
                raise IndexError(e.reason)
            raise  # pragma: no cover

    def get_value(self, cell):
        if isinstance(cell, tuple):
            cell = coord_to_cell(*cell)

        return self.get_values(cell)['values'][0][0]

    def get_range(self, range_spec=None):
        return self.get_values(range_spec)['values']

    def get_contents(self, sheet=None):
        sheet_info = self.get_sheet_info(sheet)
        gp = sheet_info['properties']['gridProperties']
        cols, rows = gp['columnCount'], gp['rowCount']
        title = sheet_info['properties']['title']

        start = 'A1'
        end = coord_to_cell(cols, rows)
        range_spec = f'{title}!{start}:{end}'
        return self.get_range(range_spec)

    def get_dictionaries(self, range_spec=None):
        rows = []
        labels = None
        for row in self.get_range(range_spec):
            if labels is None:
                labels = row
                continue
            rows.append(dict(zip(labels, row)))
        return rows
