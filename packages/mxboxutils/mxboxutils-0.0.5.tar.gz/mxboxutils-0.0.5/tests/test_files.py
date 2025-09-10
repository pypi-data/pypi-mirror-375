import os

from mx.file import all_files


def test_all_files():
    print(all_files(os.path.dirname(__file__)))
