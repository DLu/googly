from googly import SheetsAPI
from googly.apps.sheets import coord_to_cell, cell_to_coord
import pytest
from creds import get_credentials

DATA = [
    # col, row, spec
    (0, 0, 'A1'),
    (1, 0, 'B1'),
    (0, 1, 'A2'),
    (1, 1, 'B2'),
    (2, 29, 'C30'),
    (3, 41, 'D42'),
    (24, 99, 'Y100'),
    (25, 0, 'Z1'),
    (26, 0, 'AA1'),
    (27, 0, 'AB1'),
]

values = []
test_ids = []

for col, row, spec in DATA:
    values.append(((col, row), spec))
    test_ids.append(spec)


@pytest.mark.parametrize('coords, spec', values, ids=test_ids)
def test_conversion(coords, spec):
    assert coord_to_cell(*coords) == spec
    assert cell_to_coord(spec) == coords


def test_basic_access():
    api = SheetsAPI(**get_credentials())

    api.set_sheet_id('1eq8DhTowKJqPiybptG850V_kMr9336RkSo27GbJEZ3c')

    assert api.get_value('A1') == 'Name'
    assert api.get_value((0, 3)) == 'Daniel Murphy'
    assert api.get_value((26, 3)) == 10
    assert api.get_value('Pitching!E3') == 2.54

    with pytest.raises(IndexError):
        api.get_value((27, 3))

    with pytest.raises(IndexError):
        api.get_value('BB30')

    age_cells = api.get_range('Pitching!B2:B6')
    assert len(age_cells) == 5
    ages = [row[0] for row in age_cells]
    assert sum(ages) // len(ages) == 29

    for row in api.get_dictionaries('Pitching!A1:H6'):
        assert 'ERA' in row
        assert isinstance(row['ERA'], float)

    assert api.get_size() == (27, 11)
    assert api.get_size(0) == (27, 11)
    assert api.get_size('Batting') == (27, 11)
    assert api.get_size(1) == (26, 1000)
    assert api.get_size('Pitching') == (26, 1000)

    assert api.has_sheet_name('Batting')
    assert api.has_sheet_name('Pitching')
    assert not api.has_sheet_name('Fielding')

    assert api.get_sheet_name(0) == 'Batting'
    assert api.get_sheet_name(1) == 'Pitching'

    with pytest.raises(IndexError):
        api.get_size(2)

    with pytest.raises(IndexError):
        api.get_size('Fielding')

    with pytest.raises(IndexError):
        api.get_size(5.5)

    contents = api.get_contents(sheet=0)
    assert len(contents) == 11
    assert contents[0][0] == 'Name'
    assert contents[0][-1] == 'IBB'
    assert contents[2][0] == 'Lucas Duda'
    assert contents[2][10] == 27


def test_no_sheet_id():
    api = SheetsAPI(**get_credentials())
    with pytest.raises(Exception):
        api.get_value('A1')


def test_writing():
    api = SheetsAPI(**get_credentials())
    api.set_sheet_id('1QegYhRutctw5pogpJMFglHsEBTMYlUg8XGE4dvIz9iE')

    try:

        assert api.has_sheet_name('Sheet1')
        assert not api.has_sheet_name('Sheet2')

        api.clear_contents()

        alphabet_data = [
            ['A', 'B', 'C', 'D'],
            ['E', 'F', 'G', 'H'],
            ['I', 'J', 'K', 'L'],
            ['M', 'N', 'O', 'P'],
        ]

        api.set_contents(alphabet_data)
        assert api.get_value('A1') == 'A'
        assert api.get_value('B1') == 'B'
        assert api.get_value('A2') == 'E'
        assert api.get_value('C3') == 'K'
        assert api.get_value('D3') == 'L'
        assert api.get_value('D4') == 'P'

        api.clear_contents(['A1:B4'])
        assert api.get_value('A1') == ''
        assert api.get_value('B1') == ''
        assert api.get_value('A2') == ''
        assert api.get_value('C3') == 'K'
        assert api.get_value('D3') == 'L'
        assert api.get_value('D4') == 'P'

        api.set_contents(alphabet_data, row_major=False)
        assert api.get_value('A1') == 'A'
        assert api.get_value('B1') == 'E'
        assert api.get_value('A2') == 'B'
        assert api.get_value('C3') == 'K'
        assert api.get_value('D3') == 'O'
        assert api.get_value('D4') == 'P'

        api.add_sheet('Sheet2')
        assert api.has_sheet_name('Sheet1')
        assert api.has_sheet_name('Sheet2')

        # Get empty values
        grid = api.get_contents('Sheet2')
        assert len(grid) == 1000
        for row in grid:
            assert len(row) == 26
            assert all(not a for a in row)

        api.clear_contents(['Sheet1!A1:A4', 'Sheet1!C1:C4'])
        assert api.get_value('A1') == ''
        assert api.get_value('B1') == 'E'
        assert api.get_value('A2') == ''
        assert api.get_value('C3') == ''
        assert api.get_value('D3') == 'O'
        assert api.get_value('D4') == 'P'

        # Avoid duplicate insertion
        assert len(api.get_sheet_names()) == 2
        api.add_sheet('Sheet1')  # Should do nothing
        assert len(api.get_sheet_names()) == 2

    finally:
        api.delete_sheet('Sheet2')
        assert api.has_sheet_name('Sheet1')
        assert not api.has_sheet_name('Sheet2')

        api.clear_contents(sheet='Sheet1')
