# https://www.myabandonware.com/game/test-drive-di/play-di
from googly import DriveAPI
from googly.util import make_date
from creds import get_credentials


def test_basic_access():
    api = DriveAPI(**get_credentials())

    files = list(api.get_files())

    # Should be at least one file
    assert files

    sheet_id = None
    for info in files:
        if info['name'] == 'Googly Test Sheet':
            sheet_id = info['id']

    assert sheet_id

    sheet_info = api.get_file_info(sheet_id)
    assert sheet_info['kind'] == 'drive#file'
    assert sheet_info['mimeType'] == 'application/vnd.google-apps.spreadsheet'
    assert 'size' not in sheet_info
    assert 'createdTime' not in sheet_info

    sheet_info = api.get_file_info(sheet_id, fields='size, createdTime')
    assert sheet_info['size'] == 2286
    assert sheet_info['createdTime'] == make_date(2024, 4, 9, 17, 29, 5, 648000)
    assert 'kind' not in sheet_info
    assert 'mimeType' not in sheet_info
