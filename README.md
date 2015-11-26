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

## Building Paths
After authenticating a user or admin, you can build paths to your data by using the child() method.

```python
user.child("users").child("Marty")
```

## Saving Data

### PUSH

To save data with a unique, auto-generated, timestamp-based key, use the PUSH method.

```python
data = {"name": "Marty Mcfly", "date": "05-11-1955"}
admin.child("users").push(data)
```

### SET

To create your own keys use the SET method. The key in the example below is "Marty".

```python
data = {"Marty": {"name": "Marty Mcfly", "date":"05-11-1955"}}
admin.child("users").set(data)
```

### UPDATE

To update data for an existing entry use the UPDATE method.

```python
admin.child("users").child("Marty).update({"date": "26-10-1985"})
```

### REMOVE

To delete data for an existing entry use the REMOVE method.

```python
admin.child("users").remove("Marty")
```


## Reading Data

### Simple Queries

#### get

To return data from a path simply call the get() method.

```python
all_users = admin.child("users").get()
```

#### shallow

To return just the keys at a particular path use the shallow() method.

```python
all_user_ids = admin.child("users").shallow().get()
```

Note: shallow() can not be used in conjunction with any complex queries.


### Complex Queries

Queries can be built by chaining multiple query parameters together (in much the same way as they are in the [javascript library](https://www.firebase.com/docs/web/guide/retrieving-data.html#section-complex-queries)).

Example:
```python
users_by_name = admin.child("users").orderBy("name").limitToFirst(3).get()
```
This query will return the first three users ordered by name.

#### orderBy

We begin any complex query with the orderBy parameter.

Example:
```python
users_by_name = admin.child("users").orderBy("name").get()
```
This query will return users ordered by name.

#### equalTo

Return data with a specific value.

Example:
```python
users_by_score = admin.child("users").orderBy("score").equalTo(10).get()
```
This query will return users with a score of 10.

#### startAt and endAt

Specify a range in your data.

Example:
```python
users_by_score = admin.child("users").orderBy("score").startAt(3).endAt(10).get()
```
This query returns users ordered by score and with a score between 3 and 10.

#### limitToFirst and limitToLast

Limits data returned.

Example:
```python
users_by_score = admin.child("users").orderBy("score").limitToFirst(5).get()
```
This query returns the first five users ordered by score.


## Common Errors

### Index not defined

Indexing is [not enabled](https://www.firebase.com/docs/security/guide/indexing-data.html) for the database reference.

### Property types don't match

Returned properties are not of the same data type.
Example: name: 0 and name: "hello".