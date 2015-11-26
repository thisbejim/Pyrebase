from operator import itemgetter
from collections import OrderedDict
import requests
from firebase_token_generator import create_token
from urllib.parse import urlencode, quote
import re
import json


class Firebase():
    """ Firebase Interface """
    def __init__(self, fire_base_url, fire_base_secret, email=False, password=False):
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

        if email and password:
            request_ref = 'https://auth.firebase.com/auth/firebase?firebase={0}&email={1}&password={2}'.\
                format(name, email, password)
            request_object = requests.get(request_ref)
            request_json = request_object.json()
            self.email = email
            self.password = password
            self.uid = request_json['user']['uid']
            self.token = request_json['token']
        else:
            auth_payload = {"uid": "1"}
            options = {"admin": True}
            token = create_token(fire_base_secret, auth_payload, options)
            self.token = token
            self.email = None
            self. password = None
            self.uid = None

        self.fire_base_url = url
        self.fire_base_name = name
        self.secret = fire_base_secret
        self.path = ""
        self.buildQuery = {}

    def create_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = requests.get(request_ref)
        request_json = request_object.json()
        return request_json

    def remove_user(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/remove?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = requests.get(request_ref)
        request_json = request_object.json()
        return request_json

    def change_password(self, email, new_password):
        request_ref = 'https://auth.firebase.com/auth/firebase/update?firebase={0}&email={1}&newPassword={2}'.\
            format(self.fire_base_name, email, new_password)
        request_object = requests.get(request_ref)
        request_json = request_object.json()
        return request_json

    def send_password_reset_email(self, email, new_password):
        request_ref = 'https://auth.firebase.com/auth/firebase/reset_password?firebase={0}&email={1}'.\
            format(self.fire_base_name, email, new_password)
        request_object = requests.get(request_ref)
        request_json = request_object.json()
        return request_json

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
            self.path += new_path
        return self

    def get(self):
        parameters = {}
        parameters['auth'] = self.token
        for param in list(self.buildQuery):
            if type(self.buildQuery[param]) is str:
                parameters[param] = quote('"' + self.buildQuery[param] + '"')
            else:
                parameters[param] = self.buildQuery[param]
        request_ref = '{0}{1}.json?{2}'.format(self.fire_base_url, self.path, urlencode(parameters))
        print(request_ref)
        request_object = requests.get(request_ref)
        request_dict = request_object.json()
        # if primitive or simple query return
        if not isinstance(request_object.json(), dict) or not self.buildQuery:
            return request_object.json()
        # return keys if shallow is enabled
        if self.buildQuery and self.buildQuery["shallow"]:
            return request_object.json().keys()
        # otherwise sort
        results = []
        for i in request_dict:
            request_dict[i]["key"] = i
            results.append(request_dict[i])
        # sort if required
        if self.buildQuery and self.buildQuery["orderBy"]:
            if self.buildQuery["orderBy"] == "$key":
                self.buildQuery["orderBy"] = "key"
            results = sorted(results, key=itemgetter(self.buildQuery["orderBy"]))
        return results

    def info(self):
        info_list = {'url': self.fire_base_url, 'token': self.token, 'email': self.email, 'password': self.password,
                     'uid': self.uid}
        return info_list

    def push(self, data):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, self.token)
        request_object = requests.post(request_ref, data=dump(data))
        return request_object.status_code

    def set(self, data):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, self.token)
        request_object = requests.put(request_ref, data=dump(data))
        return request_object.status_code

    def update(self, data):
        request_ref = '{0}{1}.json?auth={3}'.format(self.fire_base_url, self.path, self.token)
        request_object = requests.patch(request_ref, data=dump(data))
        return request_object.status_code

    def remove(self):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, self.path, self.token)
        request_object = requests.delete(request_ref)
        return request_object.status_code


def dump(data):
    if isinstance(data, dict):
        return json.dumps(data)
    else:
        return data
