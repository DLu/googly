import googly
import googleapiclient
import re

CELL_PATTERN = re.compile(r'^([A-Z]+)(\d+)$')
RANGE_PATTERN = re.compile(r'^(.*)!(.*):(.*)$')
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
        SPREADSHEETS = 2  # Read and write

    def __init__(self, spreadsheetId=None, scopes=Scope.SPREADSHEETS, **kwargs):
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

    def get_sheet_names(self, meta=None):
        names = []
        if not meta:
            meta = self.get_metadata()
        for sheet in meta['sheets']:
            names.append(sheet['properties']['title'])
        return names

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
                names = self.get_sheet_names(meta)
                raise IndexError(f'Unable to find sheet named {sheet}. Valid names are {names}')
        else:
            raise IndexError(f'Cannot get sheet {sheet}')

    def get_sheet_name(self, sheet):
        sheet_info = self.get_sheet_info(sheet)
        return sheet_info['properties']['title']

    def has_sheet_name(self, sheet_name):
        return sheet_name in self.get_sheet_names()

    def get_size(self, sheet=None):
        sheet_info = self.get_sheet_info(sheet)
        gp = sheet_info['properties']['gridProperties']
        return gp['columnCount'], gp['rowCount']

    def get_values(self, range_spec):
        if self.sheet_id is None:
            raise Exception('Must specify spreadsheetId in constructor or by calling set_sheet_id')
        try:
            return googly.destring(self.api.values().get(spreadsheetId=self.sheet_id, range=range_spec).execute())
        except googleapiclient.errors.HttpError as e:
            if 'exceeds grid limits' in e.reason:
                raise IndexError(e.reason)
            raise  # pragma: no cover

    def get_value(self, cell):
        if isinstance(cell, tuple):
            cell = coord_to_cell(*cell)

        value_matrix = self.get_values(cell)
        if 'values' not in value_matrix:
            return ''
        else:
            return value_matrix['values'][0][0]

    def get_range(self, range_spec=None):
        ret = self.get_values(range_spec)
        if 'values' in ret:
            return ret['values']
        else:
            m = RANGE_PATTERN.match(ret['range'])
            start = cell_to_coord(m.group(2))
            end = cell_to_coord(m.group(3))

            width = end[0] - start[0] + 1
            height = end[1] - start[1] + 1
            values = []
            for h in range(height):
                values.append([''] * width)
            return values

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

    def set_contents(self, values, start_cell='A1', row_major=True, raw=False, sheet=None):
        sheet_name = self.get_sheet_name(sheet)
        c0, r0 = cell_to_coord(start_cell)
        if row_major:
            r1 = r0 + len(values) - 1
            c1 = c0 + len(values[0]) - 1
        else:
            c1 = c0 + len(values) - 1
            r1 = r0 + len(values[0]) - 1
        end_cell = coord_to_cell(c1, r1)
        range_name = f'{sheet_name}!{start_cell}:{end_cell}'

        return self.api.values().update(
            spreadsheetId=self.sheet_id,
            range=range_name,
            valueInputOption='RAW' if raw else 'USER_ENTERED',
            body={
                'range': range_name,
                'majorDimension': 'ROWS' if row_major else 'COLUMNS',
                'values': values,
            }
        ).execute()

    def clear_contents(self, ranges=None, sheet=None):
        sheet_name = self.get_sheet_name(sheet)
        full_ranges = []
        if ranges:
            for range_spec in ranges:
                if '!' in range_spec:
                    full_ranges.append(range_spec)
                else:
                    full_ranges.append(f'{sheet_name}!{range_spec}')
        else:
            col, row = self.get_size(sheet)
            end_cell = coord_to_cell(col, row)
            full_ranges.append(f'{sheet_name}!A1:{end_cell}')
        return self.api.values().batchClear(
            spreadsheetId=self.sheet_id,
            body={
                'ranges': full_ranges,
            }
        ).execute()

    def batch_update(self, requests):
        if not isinstance(requests, list):
            requests = [requests]

        return self.api.batchUpdate(
            spreadsheetId=self.sheet_id,
            body={
                'requests': requests
            }
        ).execute()

    def add_sheet(self, title=None):
        if self.has_sheet_name(title):
            return

        self.metadata = {}
        return self.batch_update({'addSheet': {'properties': {'title': title}}})

    def delete_sheet(self, sheet=None):
        sheet_info = self.get_sheet_info(sheet)
        sheet_id = sheet_info['properties']['sheetId']

        self.metadata = {}
        return self.batch_update({'deleteSheet': {'sheetId': sheet_id}})
