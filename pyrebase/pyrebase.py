import requests
from requests.exceptions import HTTPError
from firebase_token_generator import create_token
try:
    from urllib.parse import urlencode, quote
except:
    from urllib import urlencode, quote
import re
import json
import math
from random import uniform
import time
from collections import OrderedDict
from sseclient import SSEClient
import threading
import socket

class Firebase():
    """ Firebase Interface """
    def __init__(self, fire_base_url, fire_base_secret, expires=None):
        if not fire_base_url.endswith('/'):
            url = ''.join([fire_base_url, '/'])
        else:
            url = fire_base_url
        # find db name between http:// and .firebaseio.com
        db_name = re.search('https://(.*).firebaseio.com', fire_base_url)
        if db_name:
            name = db_name.group(1)
        else:
            db_name = re.search('(.*).firebaseio.com', fire_base_url)
            name = db_name.group(1)
        # default to admin
        auth_payload = {"uid": "1"}
        options = {"admin": True}
        if expires:
            options["expires"] = expires

        self.token = create_token(fire_base_secret, auth_payload, options)
        self.requests = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        for scheme in ('http://', 'https://'):
            self.requests.mount(scheme, adapter)
        self.fire_base_url = url
        self.fire_base_name = name
        self.secret = fire_base_secret
        self.path = ""
        self.build_query = {}
        self.last_push_time = 0
        self.last_rand_chars = []

    def auth_with_password(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        return request_object.json()

    def create_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def remove_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/remove?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def change_password(self, email, old_password, new_password):
        request_ref = 'https://auth.firebase.com/auth/firebase/update?' \
                      'firebase={0}&email={1}&oldPassword={2}&newPassword={3}'.\
            format(self.fire_base_name, email, old_password, new_password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def send_password_reset_email(self, email):
        request_ref = 'https://auth.firebase.com/auth/firebase/reset_password?firebase={0}&email={1}'.\
            format(self.fire_base_name, email)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def order_by_child(self, order):
        self.build_query["orderBy"] = order
        return self

    def start_at(self, start):
        self.build_query["startAt"] = start
        return self

    def end_at(self, end):
        self.build_query["endAt"] = end
        return self

    def equal_to(self, equal):
        self.build_query["equalTo"] = equal
        return self

    def limit_to_first(self, limit_first):
        self.build_query["limitToFirst"] = limit_first
        return self

    def limit_to_last(self, limit_last):
        self.build_query["limitToLast"] = limit_last
        return self

    def shallow(self):
        self.build_query["shallow"] = True
        return self

    def child(self, *args):
        new_path = "/".join(args)
        if self.path:
            self.path += "/{}".format(new_path)
        else:
            if new_path.startswith("/"):
                new_path = new_path[1:]
            self.path = new_path
        return self

    def get(self, token=None):
        build_query = self.build_query
        query_key = self.path.split("/")[-1]
        request_ref = self.build_request_url(token)
        # do request
        request_object = self.requests.get(request_ref)
        try:
            request_object.raise_for_status()
        except HTTPError as e:
            # raise detailed error message
            raise HTTPError(e, request_object.text)

        request_dict = request_object.json()
        # if primitive or simple query return
        if not isinstance(request_dict, dict):
            return PyreResponse(request_dict, query_key)
        if not build_query:
            return PyreResponse(convert_to_pyre(request_dict.items()), query_key)
        # return keys if shallow
        if build_query.get("shallow"):
            return PyreResponse(request_dict.keys(), query_key)
        # otherwise sort
        sorted_response = None
        if build_query.get("orderBy"):
            if build_query["orderBy"] == "$key":
                sorted_response = sorted(request_dict.items(), key=lambda item: item[0])
            else:
                sorted_response = sorted(request_dict.items(), key=lambda item: item[1][build_query["orderBy"]])
        return PyreResponse(convert_to_pyre(sorted_response), query_key)

    def stream(self, stream_handler, token=None):
        request_ref = self.build_request_url(token)
        return Stream(request_ref, stream_handler)

    def build_request_url(self, token):
        parameters = {}
        parameters['auth'] = check_token(token, self.token)
        for param in list(self.build_query):
            if type(self.build_query[param]) is str:
                parameters[param] = quote('"' + self.build_query[param] + '"')
            else:
                parameters[param] = self.build_query[param]
        # reset path and build_query for next query
        request_ref = '{0}{1}.json?{2}'.format(self.fire_base_url, self.path, urlencode(parameters))
        self.path = ""
        self.build_query = {}
        return request_ref

    def push(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.post(request_ref, data=json.dumps(data))
        return request_object.json()

    def set(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.put(request_ref, data=json.dumps(data))
        return request_object.json()

    def update(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.patch(request_ref, data=json.dumps(data))
        return request_object.json()

    def remove(self, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.delete(request_ref)
        return request_object.json()

    def generate_key(self):
        push_chars = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        now = int(time.time() * 1000)
        duplicate_time = now == self.last_push_time
        self.last_push_time = now
        time_stamp_chars = [0] * 8
        for i in reversed(range(0, 8)):
            time_stamp_chars[i] = push_chars[now % 64]
            now = math.floor(now / 64)
        new_id = "".join(time_stamp_chars)
        if not duplicate_time:
            for i in range(0, 12):
                self.last_rand_chars.append(math.floor(uniform(0, 1) * 64))
        else:
            for i in range(0, 11):
                if self.last_rand_chars[i] == 63:
                    self.last_rand_chars[i] = 0
                self.last_rand_chars[i] += 1
        for i in range(0, 12):
            new_id += push_chars[self.last_rand_chars[i]]
        return new_id

    def sort(self, origin, by_key):
        # unpack pyre objects
        pyres = origin.each()
        new_list = []
        for pyre in pyres:
            new_list.append(pyre.item)
        # sort
        data = sorted(dict(new_list).items(), key=lambda item: item[1][by_key])
        return PyreResponse(convert_to_pyre(data), origin.key())


def convert_to_pyre(items):
    pyre_list = []
    for item in items:
        pyre_list.append(Pyre(item))
    return pyre_list


class PyreResponse:
    def __init__(self, pyres, query_key):
        self.pyres = pyres
        self.query_key = query_key

    def val(self):
        if isinstance(self.pyres, list):
            # unpack pyres into OrderedDict
            pyre_list = []
            for pyre in self.pyres:
                pyre_list.append((pyre.key(), pyre.val()))
            return OrderedDict(pyre_list)
        else:
            # return primitive or simple query results
            return self.pyres

    def key(self):
        return self.query_key

    def each(self):
        if isinstance(self.pyres, list):
            return self.pyres


class Pyre:
    def __init__(self, item):
        self.item = item

    def val(self):
        return self.item[1]

    def key(self):
        return self.item[0]


class ClosableSSEClient(SSEClient):
    def __init__(self, *args, **kwargs):
        self.should_connect = True
        super(ClosableSSEClient, self).__init__(*args, **kwargs)

    def _connect(self):
        if self.should_connect:
            super(ClosableSSEClient, self)._connect()
        else:
            raise StopIteration()

    def close(self):
        self.should_connect = False
        self.retry = 0
        self.resp.raw._fp.fp.raw._sock.shutdown(socket.SHUT_RDWR)
        self.resp.raw._fp.fp.raw._sock.close()


class Stream:
    def __init__(self, url, stream_handler):
        self.url = url
        self.stream_handler = stream_handler
        self.sse = None
        self.thread = None
        self.start()

    def start(self):
        self.thread = threading.Thread(target=self.start_stream,
                                       args=(self.url, self.stream_handler))
        self.thread.start()
        return self

    def start_stream(self, url, stream_handler):
        self.sse = ClosableSSEClient(url)
        for msg in self.sse:
            msg_data = json.loads(msg.data)
            # don't return initial data
            if msg_data and msg_data['path'] != '/':
                msg_data["event"] = msg.event
                stream_handler(msg_data)

    def close(self):
        self.sse.close()
        self.thread.join()
        return self


def check_token(user_token, admin_token):
    if user_token:
        return user_token
    else:
        return admin_token
