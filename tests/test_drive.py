# https://www.myabandonware.com/game/test-drive-di/play-di
from googly import DriveAPI
from googly.util import make_date
from creds import get_credentials
import tempfile
import pathlib


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


def test_walk():
    api = DriveAPI(**get_credentials())

    walk_results = list(api.walk('1gVDQMGLTHQwTEBZhDP6ibsvkpcR2SIhv'))

    assert len(walk_results) == 4

    # Test Roots (searched in alphabetical depth first)
    roots = [el[0] for el in walk_results]
    assert roots[0] == ''
    assert roots[1] == 'TestFolderB'
    assert roots[2] == 'TestFolderB/TestFolderD'
    assert roots[3] == 'TestFolderC'

    # Test Folder Lists
    folder_lists = [el[1] for el in walk_results]
    assert set(folder_lists[0].values()) == {'TestFolderB', 'TestFolderC'}
    assert set(folder_lists[1].values()) == {'TestFolderD'}
    assert not folder_lists[2].values()  # no subfolders
    assert not folder_lists[3].values()  # no subfolders

    # Test File Lists
    filename_lists = [el[2] for el in walk_results]
    assert set(filename_lists[0].values()) == {'mario.txt'}
    assert set(filename_lists[1].values()) == {'link.txt'}
    assert set(filename_lists[2].values()) == {'pika.gif'}
    assert set(filename_lists[3].values()) == {'dk.csv'}


def test_file_contents():
    api = DriveAPI(**get_credentials())
    ret = api.get_file_contents('1aQMYuq2fX7_WuhpLRhFFhMZdrNDa84NI')
    assert ret.decode() == "It's a me!\n"


def test_downloads():
    api = DriveAPI(**get_credentials())

    src_files = pathlib.Path('tests/files')

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        assert not list(temp_path.iterdir())  # Assert empty folder

        api.download_folder('1gVDQMGLTHQwTEBZhDP6ibsvkpcR2SIhv', temp_dir, dry_run=True, quiet=True)
        assert not list(temp_path.iterdir())  # Assert still empty folder

        def file_check(filepath):
            assert filepath.exists()
            ref_contents = open(src_files / filepath.name, 'rb').read()
            contents = open(filepath, 'rb').read()
            assert ref_contents == contents

        api.download_folder('1gVDQMGLTHQwTEBZhDP6ibsvkpcR2SIhv', temp_dir)
        file_check(temp_path / 'mario.txt')
        file_check(temp_path / 'TestFolderB' / 'link.txt')
        file_check(temp_path / 'TestFolderB' / 'TestFolderD' / 'pika.gif')
        file_check(temp_path / 'TestFolderC' / 'dk.csv')

        # Should download zero files
        api.download_folder('1gVDQMGLTHQwTEBZhDP6ibsvkpcR2SIhv', temp_dir)


def test_path():
    api = DriveAPI(**get_credentials())

    # Check pika.gif
    path = api.get_path('1YqKDODCT1Rb2q8wYTTb374QOcLxRGn3W')
    assert path == ['My Drive', 'TestFolderA', 'TestFolderB', 'TestFolderD']

    # Check link.txt - should hit the cache
    path = api.get_path('1h2Fkt1hI96PA6C11CT296E060A2opLNT')
    assert path == ['My Drive', 'TestFolderA', 'TestFolderB']
