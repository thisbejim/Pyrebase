from tests.tools import make_db


def test_setup():
    db = make_db(True)
    assert db.get()
