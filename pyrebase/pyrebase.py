from operator import itemgetter
from requests_futures.sessions import FuturesSession
from firebase_token_generator import create_token
from urllib.parse import urlencode, quote
import re
import json
request = FuturesSession()


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
            request_object = request.get(request_ref).result()
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
        self.child = ""
        self.buildQuery = {}

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

    def query(self, *args):
        self.child = "/".join(args)
        return self

    def get(self):
        parameters = {}
        parameters['auth'] = self.token
        for param in list(self.buildQuery):
            if type(self.buildQuery[param]) is str:
                parameters[param] = quote('"' + self.buildQuery[param] + '"')
            else:
                parameters[param] = self.buildQuery[param]
        request_ref = '{0}{1}.json?{2}'.format(self.fire_base_url, self.child, urlencode(parameters))
        request_object = request.get(request_ref).result()
        request_dict = json.loads(str(request_object.text))
        # if only one result return dict
        if not isinstance(list(request_dict.values())[0], dict):
            return request_dict
        # otherwise place in list
        results = []
        for i in request_dict:
            request_dict[i]["key"] = i
            results.append(request_dict[i])
        # sort if required
        if self.buildQuery and self.buildQuery["orderBy"]:
            if self.buildQuery["orderBy"] == "$key":
                self.buildQuery["orderBy"] = "key"
            results = sorted(results, key=itemgetter(self.buildQuery["orderBy"]))
        # return keys if shallow is enabled
        if self.buildQuery and self.buildQuery["shallow"]:
            return results.keys()
        return results

    def info(self):
        info_list = {'url': self.fire_base_url, 'token': self.token, 'email': self.email, 'password': self.password,
                     'uid': self.uid}
        return info_list

    def create(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = request.get(request_ref).result()
        request_json = request_object.json()
        return request_json

    def keys(self, child):
        request_ref = '{0}{1}.json?auth={2}&shallow=true'.\
            format(self.fire_base_url, child, self.token)

        request_object = request.get(request_ref).result()

        request_json = request_object.json()

        if request_object.status_code != 200:
            return request_json

        return request_json.keys()

    def post(self, child, data):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, child, self.token)
        request_object = request.post(request_ref, data=data).result()
        return request_object.status_code

    def put(self, child, data):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, child, self.token)
        request_object = request.put(request_ref, data=data).result()
        return request_object.status_code

    def patch(self, child, item_id, data):
        request_ref = '{0}{1}/{2}.json?auth={3}'.format(self.fire_base_url, child, item_id, self.token)
        request_object = request.patch(request_ref, data=data).result()
        return request_object.status_code

    def delete(self, child):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, child, self.token)
        request_object = request.delete(request_ref).result()
        return request_object.status_code
