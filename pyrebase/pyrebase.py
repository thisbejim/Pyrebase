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


def initialize_app(config):
    return Firebase(config)


class Firebase():
    """ Firebase Interface """
    def __init__(self, config):
        self.api_key = config["apiKey"]
        self.auth_domain = config["authDomain"]
        self.database_url = config["databaseURL"]
        self.storage_bucket = config["storageBucket"]
        self.requests = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        for scheme in ('http://', 'https://'):
            self.requests.mount(scheme, adapter)

    def auth(self):
        return Auth(self.api_key, self.requests)

    def database(self):
        return Database(self.api_key, self.database_url, self.requests)

    def storage(self):
        return Storage(self.storage_bucket, self.requests)


class Auth():
    """ Auth Interface """
    def __init__(self, api_key, requests):
        self.api_key = api_key
        self.current_user = None
        self.requests = requests

    def sign_in_with_email_and_password(self, email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        self.current_user = request_object.json()
        return request_object.json()

    def get_account_info(self, id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        return request_object.json()

    def send_email_verification(self, id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        return request_object.json()

    def send_password_reset_email(self, email):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
        request_object = requests.post(request_ref, headers=headers, data=data)
        return request_object.json()

    def verify_password_reset_code(self, reset_code, new_password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/resetPassword?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"oobCode": reset_code, "newPassword": new_password})
        request_object = requests.post(request_ref, headers=headers, data=data)
        return request_object.json()

    def create_user_with_email_and_password(self, email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8" }
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.get(request_ref, headers=headers, data=data)
        request_object.raise_for_status()
        return request_object.json()


class Database():
    """ Database Interface """
    def __init__(self, api_key, database_url, requests):

        if not database_url.endswith('/'):
            url = ''.join([database_url, '/'])
        else:
            url = database_url

        self.api_key = api_key
        self.database_url = url
        self.requests = requests

        self.path = ""
        self.build_query = {}
        self.last_push_time = 0
        self.last_rand_chars = []

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

    def build_request_url(self, token):
        parameters = {}
        parameters['auth'] = token
        for param in list(self.build_query):
            if type(self.build_query[param]) is str:
                parameters[param] = quote('"' + self.build_query[param] + '"')
            else:
                parameters[param] = self.build_query[param]
        # reset path and build_query for next query
        request_ref = '{0}{1}.json?{2}'.format(self.database_url, self.path, urlencode(parameters))
        self.path = ""
        self.build_query = {}
        return request_ref

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

    def push(self, data, token):
        request_ref = '{0}{1}.json?auth={2}'.format(self.database_url, self.path, token)
        self.path = ""
        headers = {"content-type": "application/json; charset=UTF-8" }
        request_object = self.requests.post(request_ref, headers=headers, data=json.dumps(data))
        return request_object.json()

    def set(self, data, token):
        request_ref = '{0}{1}.json?auth={2}'.format(self.database_url, self.path, token)
        self.path = ""
        request_object = self.requests.put(request_ref, data=json.dumps(data))
        return request_object.json()

    def update(self, data, token):
        request_ref = '{0}{1}.json?auth={2}'.format(self.database_url, self.path, token)
        self.path = ""
        request_object = self.requests.patch(request_ref, data=json.dumps(data))
        return request_object.json()

    def remove(self, token):
        request_ref = '{0}{1}.json?auth={2}'.format(self.database_url, self.path, token)
        self.path = ""
        request_object = self.requests.delete(request_ref)
        return request_object.json()

    def stream(self, stream_handler, token):
        request_ref = self.build_request_url(token)
        return Stream(request_ref, stream_handler)

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


class Storage():
    def __init__(self, storage_bucket, requests):
        self.storage_bucket = "https://firebasestorage.googleapis.com/v0/b/" + storage_bucket
        self.requests = requests

    def put(self, file_path, file_name, token):
        file = open(file_path, 'rb')
        request_ref = self.storage_bucket + "/o?name={0}".format(file_name)
        headers = {"Authorization": "Firebase "+token}
        request_object = self.requests.put(request_ref, headers=headers, data=file)
        return request_object.json()


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
