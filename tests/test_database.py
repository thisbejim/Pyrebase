import datetime
import random
import time
from contextlib import contextmanager

import pytest


@pytest.fixture(scope='function')
def db_sa(db):
    # To make it easier to test, we keep the test restricted to firebase_tests
    # Because of the current mutations on calls, we return it as a function.
    name = 'test_%05d' % random.randint(0, 99999)
    yield lambda: db().child(name)


@contextmanager
def make_stream(db, cbk):
    s = db.stream(cbk)
    try:
        yield s
    finally:
        s.close()


@contextmanager
def make_append_stream(db):
    l = []

    def cbk(event):
        l.append(event)

    with make_stream(db, cbk) as s:
        yield s, l


class TestSimpleGetAndPut:
    def test_simple_get(self, db_sa):
        assert db_sa().get().val() is None

    def test_put_succeed(self, db_sa):
        assert db_sa().set(True)

    def test_put_then_get_keeps_value(self, db_sa):
        db_sa().set("some_value")
        assert db_sa().get().val() == "some_value"

    def test_put_dictionary(self, db_sa):
        v = dict(a=1, b="2", c=dict(x=3.1, y="3.2"))
        db_sa().set(v)

        assert db_sa().get().val() == v

    @pytest.mark.skip
    def test_put_deeper_dictionnary(self, db_sa):
        v = {'1': {'11': {'111': 42}}}
        db_sa().set(v)

        # gives: assert [None, {'11': {'111': 42}}] == {'1': {'11': {'111': 42}}}
        assert db_sa().get().val() == v


class TestJsonKwargs:

    def encoder(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                '__type__': obj.__class__.__name__,
                'value': obj.timestamp(),
            }
        return obj

    def decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == datetime.datetime.__name__:
            return datetime.datetime.utcfromtimestamp(obj['value'])
        return obj

    def test_put_fail(self, db_sa):
        v = {'some_datetime': datetime.datetime.now()}
        with pytest.raises(TypeError):
            db_sa().set(v)

    def test_put_succeed(self, db_sa):
        v = {'some_datetime': datetime.datetime.now()}
        assert db_sa().set(v, json_kwargs={'default': str})

    def test_put_then_get_succeed(self, db_sa):
        v = {'another_datetime': datetime.datetime.now()}
        db_sa().set(v, json_kwargs={'default': self.encoder})
        assert db_sa().get(json_kwargs={'object_hook': self.decoder}).val() == v


class TestChildNavigation:
    def test_get_child_none(self, db_sa):
        assert db_sa().child('lorem').get().val() is None

    def test_get_child_after_pushing_data(self, db_sa):
        db_sa().set({'lorem': "a", 'ipsum': 2})

        assert db_sa().child('lorem').get().val() == "a"
        assert db_sa().child('ipsum').get().val() == 2

    def test_update_child(self, db_sa):
        db_sa().child('child').update({'c1/c11': 1, 'c1/c12': 2, 'c2': 3})

        assert db_sa().child('child').child('c1').get().val() == {'c11': 1, 'c12': 2}
        assert db_sa().child('child').child('c2').get().val() == 3

    def test_path_equivalence(self, db_sa):
        db_sa().set({'1': {'11': {'111': 42}}})

        assert db_sa().child('1').child('11').child('111').get().val() == 42
        assert db_sa().child('1/11/111').get().val() == 42
        assert db_sa().child('1', '11', '111').get().val() == 42
        assert db_sa().child(1, '11', '111').get().val() == 42


class TestStreaming:
    def test_create_stream_succeed(self, db_sa):
        with make_append_stream(db_sa()) as (stream, l):
            assert stream is not None

    def test_does_initial_call(self, db_sa):
        with make_append_stream(db_sa()) as (stream, l):
            time.sleep(2)
            assert len(l) == 1

    def test_responds_to_update_calls(self, db_sa):
        with make_append_stream(db_sa()) as (stream, l):
            db_sa().set({"1": "a", "1_2": "b"})
            db_sa().update({"2": "c"})
            db_sa().push("3")

            time.sleep(2)

            assert len(l) == 3
