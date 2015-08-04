from operator import itemgetter
from requests_futures.sessions import FuturesSession
from firebase_token_generator import create_token
import re

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

    def all(self, child):
        request_ref = '{0}{1}.json?auth={2}'.\
            format(self.fire_base_url, child, self.token)

        request_object = request.get(request_ref).result()

        request_json = request_object.json()

        if request_object.status_code != 200:
            return request_json

        request_list = []

        # put dictionary in list
        for i in request_json:
            # add ID key and assign id
            request_json[i]["id"] = i
            request_list.append(request_json[i])

        return request_list

    def one(self, child, item_id):
        request_ref = '{0}{1}/{2}.json?auth={3}'.\
            format(self.fire_base_url, child, item_id, self.token)

        request_object = request.get(request_ref).result()

        request_json = request_object.json()

        if request_object.status_code != 200:
            return request_json

        request_list = []

        request_json["id"] = item_id
        request_list.append(request_json)

        return request_list

    def sort(self, child, prop, start=None, limit=None, direction=None):
        if start and limit and direction:
            if direction == "last":
                direction = "limitToLast"
                at = "startAt"
            else:
                direction = "limitToFirst"
                at = "endAt"
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&{4}={5}&{6}={7}'.\
                format(self.fire_base_url, child, self.token, prop, at, start, direction, limit)
        else:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"'.\
                format(self.fire_base_url, child, self.token, prop)

        request_object = request.get(request_ref).result()
        request_json = request_object.json()
        if request_object.status_code != 200:
            return request_json

        request_list = []
        # put dictionary in list for sorting
        for i in request_json:
            # add ID key and assign id
            request_json[i]["id"] = i
            request_list.append(request_json[i])

        # sort list by category
        try:
            if direction == "limitToLast":
                request_list = sorted(request_list, key=itemgetter(prop), reverse=True)
            else:
                request_list = sorted(request_list, key=itemgetter(prop))
        except TypeError:
            raise TypeError("Property types don't match.")

        return request_list

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

