# Google Sheets

## Identifying Sheets

When you open a spreadsheet in the browser the link will look something like `https://docs.google.com/spreadsheets/d/1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c/edit#gid=0`

The bit between the `/d/` and `/edit` is the sheet id.

Rather than providing this magic identifier to each method, the sheet id is set with the `set_sheet_id` method, and then assumed to have that value until it is called again.

The test spreadsheet we're working with is [here](https://docs.google.com/spreadsheets/d/1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c/edit?usp=sharing) and contains information about the 2015 New York Mets.

## Reading a Value
```python
from googly import SheetsAPI
api = SheetsAPI()
api.set_sheet_id('1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c')
assert api.get_value('Batting!A4') == 'Daniel Murphy'
assert api.get_value((0, 3)) == 'Daniel Murphy'
```

There are multiple ways to provide [the cell coordinates](https://developers.google.com/sheets/api/guides/concepts#cell).
 * **A1 Notation** - This is the "standard" way to refer to cells in a spreadsheet, which consists of the column specified as one or more letters, and the row, specified by a number, with an optional prefix of the specific sheet/tab and an exclamation point.
 * **Python-y Coordinates** - A zero-indexed tuple for the column and row.

## Reading a Range of Values
```python
from googly import SheetsAPI
api = SheetsAPI()
api.set_sheet_id('1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c')
for row in api.get_range('Pitching!A2:B6'):
    print('{} was {} years old in 2015'.format(*row))
```

This returns the text contents of each cell, in row major order, i.e. the first thing returned is an array containing the values of the first specified row.

## Reading Dictionaries
To get an experience similar to `csv.DictReader`, you can use `get_dictionaries`

```python
from googly import SheetsAPI
api = SheetsAPI()
api.set_sheet_id('1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c')
for row in api.get_dictionaries('Pitching'):
    print(row)
```
This will use the first row as column headings and create dictionaries with the rest of the rows. The first thing printed is
```python
{'Name': 'Bartolo Colón', 'Age': '42', 'W': '14', 'L': '13', 'ERA': '4.16', 'G': '33', 'IP': '194.2', 'H': '217'}
```
