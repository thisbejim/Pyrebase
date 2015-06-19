from operator import itemgetter
from requests_futures.sessions import FuturesSession
from firebase_token_generator import create_token

request = FuturesSession()

class Firebase():
    """ Firebase Interface """
    def __init__(self, firebase_url, firebase_secret):

        if not firebase_url.endswith('/'):
            url = ''.join([firebase_url, '/'])
        else:
            url = firebase_url

        # get auth token
        auth_payload = {"uid": "1", "auth_data": "foo", "other_auth_data": "bar"}
        # disregard security rules
        options = {"admin": True}
        token = create_token(firebase_secret, auth_payload, options)

        self.fire_base_url = url
        self.token = token

    def info(self):
        return self.fire_base_url, self.token

    def all(self, child, callback):
        request_ref = '{0}{1}.json?auth={2}'.\
            format(self.fire_base_url, child, self.token)

        request_object = request.get(request_ref, background_callback=callback).result()

        request_json = request_object.json()

        if request_object.status_code != 200:
            raise ValueError(request_json)

        request_list = []

        # put dictionary in list
        for i in request_json:
            # add ID key and assign id
            request_json[i]["id"] = i
            request_list.append(request_json[i])

        return request_list

    def one(self, child, item_id, callback):
        request_ref = '{0}{1}/{2}.json?auth={3}'.\
            format(self.fire_base_url, child, item_id, self.token)

        request_object = request.get(request_ref, background_callback=callback).result()

        request_json = request_object.json()

        if request_object.status_code != 200:
            raise ValueError(request_json)

        request_list = []

        request_json["id"] = item_id
        request_list.append(request_json)

        return request_list

    def sort_by(self, child, category, callback):
        if category:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"'.\
                format(self.fire_base_url, child, self.token, category)
        else:
            request_ref = '{0}{1}.json?auth={2}'.\
                format(self.fire_base_url, child, self.token)

        request_object = request.get(request_ref, background_callback=callback).result()
        request_json = request_object.json()
        if request_object.status_code != 200:
            raise ValueError(request_json)

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
            raise TypeError("Firebase category data type doesn't match across all entities.")

        return request_list

    def sort_by_first(self, child, category, start_at, limit_to_first, callback):

        request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&startAt={4}&limitToFirst={5}'.\
            format(self.fire_base_url, child, self.token, category, start_at, limit_to_first)

        request_object = request.get(request_ref, background_callback=callback).result()
        request_json = request_object.json()

        if request_object.status_code != 200:
            raise ValueError(request_json)

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
            raise TypeError("Data type doesn't match across entities.")

        return request_list

    def sort_by_last(self, child, category, start_at, limit_to_last, callback):
        if start_at:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&endAt={4}&limitToLast={5}'.\
                format(self.fire_base_url, child, self.token, category, start_at, limit_to_last)
        else:
            request_ref = '{0}{1}.json?auth={2}&orderBy="{3}"&limitToLast={4}'.\
                format(self.fire_base_url, child, self.token, category, limit_to_last)

        request_object = request.get(request_ref, background_callback=callback).result()
        request_json = request_object.json()

        if request_object.status_code != 200:
            raise ValueError(request_json)

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
            raise TypeError("Firebase category data type doesn't match across all entities.")

        return request_list

    def post(self, child, data, callback):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, child, self.token)
        request_object = request.post(request_ref, data=data, background_callback=callback).result()
        return request_object.status_code

    def put(self, child, data, callback):
        request_ref = '{0}{1}.json?auth={2}'.format(self.fire_base_url, child, self.token)
        request_object = request.put(request_ref, data=data, background_callback=callback).result()
        return request_object.status_code

    def patch(self, child, item_id, data, callback):
        request_ref = '{0}{1}/{2}.json?auth={3}'.format(self.fire_base_url, child, item_id, self.token)
        request_object = request.patch(request_ref, data=data, background_callback=callback).result()
        return request_object.status_code

