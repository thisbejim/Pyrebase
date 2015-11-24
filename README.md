# [Pyrebase](https://pypi.python.org/pypi/Pyrebase)

A simple python wrapper for the [Firebase API](https://www.firebase.com/docs/rest/guide/).

## Installation

```python
pip install pyrebase
```


## Initialising your Firebase

### Admin

Authenticating as an admin will disregard your security rules.

```python
admin = pyrebase.Firebase('https://yourfirebaseurl.firebaseio.com', 'yourfirebasesecret')
```

### Users

#### Creating new users

```python
new_user_info = admin.create('email', 'password')
```

#### Authenticate a user

Initialise your Firebase with an additional email and password. Security rules apply to this connection type.

```python
user = pyrebase.Firebase('https://yourfirebaseurl.firebaseio.com', 'yourfirebasesecret', 'email', 'password')
```

### Connection Info

Learn more about your current connection.

```python
print(user.info['uid']) # -K2QRiOt8oQ5vBYS5mI1
```


## Saving Data

### POST

To save data with a unique, auto-generated, timestamp-based key, use the POST method.

```python
import json
data = {"name": "Marty Mcfly", "date": "05-11-1955"}
admin.post("users", json.dumps(data))
```

### PUT

To create your own keys use the PUT method. The key in the example below is "Marty".

```python
import json
data = {"Marty": {"name": "Marty Mcfly", "date":"05-11-1955"}}
admin.put("users", json.dumps(data))
```

### PATCH

To update data for an existing entry use the PATCH method.

```python
import json
data = {"date": "26-10-1985"}
admin.patch("users", "Marty", json.dumps(data))
```

### DELETE

To delete data for an existing entry use the DELETE method.

```python
admin.delete("users/Marty")
```


## Reading Data

### Simple Queries

#### query

Takes a database reference, returning all reference data.

```python
all_users = admin.query("users").get()
```

To retrieve one entry just expand the path.

```python
one_user = admin.query("users/Marty").get()
```

#### keys

Takes a database reference, returning all keys beneath that point. This does not get the full tree of data from Firebase.

```python
all_user_ids = admin.keys("users")
```


### Complex Queries

Queries can be chained in much the same way that they are in the [javascript library](https://www.firebase.com/docs/web/guide/retrieving-data.html#section-complex-queries).

Docs coming...

#### orderBy

#### equalTo

#### startAt

#### endAt

#### limitToFirst

#### limitToLast

## Common Errors

### Index not defined

Indexing is [not enabled](https://www.firebase.com/docs/security/guide/indexing-data.html) for the database reference.

### Property types don't match

Returned properties are not of the same data type.
Example: name: 0 and name: "hello".