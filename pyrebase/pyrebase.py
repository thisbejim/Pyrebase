from operator import itemgetter
from requests_futures.sessions import FuturesSession
from firebase_token_generator import create_token
import re

request = FuturesSession()


class Firebase():
    """ Firebase Interface """
    def __init__(self, fire_base_url, fire_base_secret, uid=False):

        if not fire_base_url.endswith('/'):
            url = ''.join([fire_base_url, '/'])
        else:
            url = fire_base_url

        result = re.search('https://(.*).firebaseio.com', fire_base_url)
        if result:
            name = result.group(1)
        else:
            result = re.search('(.*).firebaseio.com', fire_base_url)
            name = result.group(1)

        if uid:
            # get auth token
            auth_payload = {"uid": uid}
            # generate user token
            token = create_token(fire_base_secret, auth_payload)
        else:
            auth_payload = {"uid": "1"}
            options = {"admin": True}
            token = create_token(fire_base_secret, auth_payload, options)

        self.fire_base_url = url
        self.fire_base_name = name
        self.secret = fire_base_secret
        self.token = token

    def info(self):
        return self.fire_base_url, self.token

    def create(self, email, password):
        request_ref = 'https://auth.firebase.com/auth/firebase/create?firebase={0}&email={1}&password={2}'.\
            format(self.fire_base_name, email, password)
        request_object = request.get(request_ref).result()
        return request_object.text

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

    def sort_by(self, child, category):
        if category:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"'.\
                format(self.fire_base_url, child, self.token, category)
        else:
            request_ref = '{0}{1}.json?auth={2}'.\
                format(self.fire_base_url, child, self.token)

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
            request_list = sorted(request_list, key=itemgetter(category))
        except TypeError:
            raise TypeError("Property types don't match.")

        return request_list

    def sort_by_first(self, child, category, start_at, limit_to_first):

        request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&startAt={4}&limitToFirst={5}'.\
            format(self.fire_base_url, child, self.token, category, start_at, limit_to_first)

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
            request_list = sorted(request_list, key=itemgetter(category))
        except TypeError:
            raise TypeError("Property types don't match.")

        return request_list

    def sort_by_last(self, child, category, start_at, limit_to_last):
        if start_at:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&endAt={4}&limitToLast={5}'.\
                format(self.fire_base_url, child, self.token, category, start_at, limit_to_last)
        else:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&limitToLast={4}'.\
                format(self.fire_base_url, child, self.token, category, limit_to_last)

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
            request_list = sorted(request_list, key=itemgetter(category), reverse=True)
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

