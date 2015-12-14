from operator import itemgetter
import requests
from requests.exceptions import HTTPError
from firebase_token_generator import create_token
from urllib.parse import urlencode, quote
import re
import json
import math
from random import uniform
import time


class Firebase():
    """ Firebase Interface """
    def __init__(self, fire_base_url, fire_base_secret):
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

        self.token = create_token(fire_base_secret, auth_payload, options)
        self.requests = requests.Session()
        self.fire_base_url = url
        self.fire_base_name = name
        self.secret = fire_base_secret
        self.path = ""
        self.buildQuery = {}
        self.last_push_time = 0
        self.last_rand_chars = []

    def authWithPassword(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        return request_object.json()

    def createUser(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def removeUser(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/remove?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def changePassword(self, email, old_password, new_password):
        request_ref = 'https://auth.firebase.com/auth/firebase/update?' \
                      'firebase={0}&email={1}&oldPassword={2}&newPassword={3}'.\
            format(self.fire_base_name, email, old_password, new_password)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def sendPasswordResetEmail(self, email):
        request_ref = 'https://auth.firebase.com/auth/firebase/reset_password?firebase={0}&email={1}'.\
            format(self.fire_base_name, email)
        request_object = self.requests.get(request_ref)
        request_object.raise_for_status()
        return request_object.json()

    def orderBy(self, order):
        self.buildQuery["orderBy"] = order
        return self

    def startAt(self, start):
        self.buildQuery["startAt"] = start
        return self

    def endAt(self, end):
        self.buildQuery["endAt"] = end
        return self

    def equalTo(self, equal):
        self.buildQuery["equalTo"] = equal
        return self

    def limitToFirst(self, limitFirst):
        self.buildQuery["limitToLast"] = limitFirst
        return self

    def limitToLast(self, limitLast):
        self.buildQuery["limitToLast"] = limitLast
        return self

    def shallow(self):
        self.buildQuery["shallow"] = True
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
        parameters = {}
        parameters['auth'] = check_token(token, self.token)
        for param in list(self.buildQuery):
            if type(self.buildQuery[param]) is str:
                parameters[param] = quote('"' + self.buildQuery[param] + '"')
            else:
                parameters[param] = self.buildQuery[param]
        request_ref = '{0}{1}.json?{2}'.format(self.fire_base_url, self.path, urlencode(parameters))
        # reset path and buildQuery for next query
        self.path = ""
        buildQuery = self.buildQuery
        self.buildQuery = {}
        # do request
        request_object = self.requests.get(request_ref)
        # return if error
        try:
            request_object.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e, request_object.text)

        request_dict = request_object.json()
        # if primitive or simple query return
        if not isinstance(request_dict, dict):
            return request_dict
        if not buildQuery:
            return request_dict.values()
        # return keys if shallow is enabled
        if buildQuery.get("shallow"):
            return request_dict.keys()
        # otherwise sort
        if buildQuery.get("orderBy"):
            if buildQuery["orderBy"] in ["$key", "key"]:
                return sorted(list(request_dict))
            else:
                return sorted(request_dict.values(), key=itemgetter(buildQuery["orderBy"]))

    def push(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.post(request_ref, data=dump(data))
        return request_object.json()

    def set(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.put(request_ref, data=dump(data))
        return request_object.json()

    def update(self, data, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.patch(request_ref, data=dump(data))
        return request_object.json()

    def remove(self, token=None):
        request_token = check_token(token, self.token)
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, request_token)
        self.path = ""
        request_object = self.requests.delete(request_ref)
        return request_object.json()

    def generateKey(self):
        PUSH_CHARS = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        now = int(time.time() * 1000)
        duplicate_time = now == self.last_push_time
        self.last_push_time = now
        time_stamp_chars = [0] * 8
        for i in reversed(range(0, 8)):
            time_stamp_chars[i] = PUSH_CHARS[now % 64]
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
            new_id += PUSH_CHARS[self.last_rand_chars[i]]
        return new_id

    def reSort(self, data, by_key):
        return sorted(data, key=itemgetter(by_key))


def dump(data):
    if isinstance(data, dict):
        return json.dumps(data)
    else:
        return data


def check_token(user_token, admin_token):
    if user_token:
        return user_token
    else:
        return admin_token
