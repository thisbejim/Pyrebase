# Pyrebase [![PyPI version](https://badge.fury.io/py/Pyrebase.svg)](https://badge.fury.io/py/Pyrebase)

A simple python wrapper for the [Firebase API](https://www.firebase.com/docs/rest/guide/).

## Installation

```python
pip install pyrebase
```


## Initialising your Firebase

```python
ref = pyrebase.Firebase('https://yourfirebaseurl.firebaseio.com', 'yourfirebasesecret')
```

## Authentication

Pyrebase will authenticate as an admin by default, disregarding [security rules](https://www.firebase.com/docs/security/guide/).

### authWithPassword

The authWithPassword method will return user data including a token you can use to adhere to security rules.

Each of the following methods accepts an optional user token: get(), push(), set(), update(), and remove().

```python
user = ref.authWithPassword("email", "password")
data = {
    "date": "26-10-1985"
}
results = ref.child("users").child("Marty").update(data, user["token"])
```

## Building Paths
You can build paths to your data by using the child() method.

```python
ref.child("users").child("Marty")
```

## Saving Data

### PUSH

To save data with a unique, auto-generated, timestamp-based key, use the PUSH method.

```python
data = {"name": "Marty Mcfly", "date": "05-11-1955"}
ref.child("users").push(data)
```

### SET

To create your own keys use the SET method. The key in the example below is "Marty".

```python
data = {"Marty": {"name": "Marty Mcfly", "date":"05-11-1955"}}
ref.child("users").set(data)
```

### UPDATE

To update data for an existing entry use the UPDATE method.

```python
ref.child("users").child("Marty").update({"date": "26-10-1985"})
```

### REMOVE

To delete data for an existing entry use the REMOVE method.

```python
ref.child("users").child("Marty").remove()
```

### MULTI-LOCATION UPDATES

You can also perform [multi-location updates](https://www.firebase.com/blog/2015-09-24-atomic-writes-and-more.html) with the update method.

```python
data = {
    "users/Marty/": {
        "date": "26-10-1985"
    },
    "users/Doc/": {
        "date": "26-10-1985",
    }
}

ref.update(data)
```

To perform multi-location writes to new locations with auto-generated keys we can use the generate_key() method.

```python
data = {
    "users/"+ref.generateKey(): {
        "date": "26-10-1985"
    },
    "users/"+ref.generateKey(): {
        "date": "26-10-1985"
    }
}

ref.update(data)
```

## Simple Queries

#### get

To return data from a path simply call the get() method.

```python
all_users = ref.child("users").get()
```

#### shallow

To return just the keys at a particular path use the shallow() method.

```python
all_user_ids = ref.child("users").shallow().get()
```

Note: shallow() can not be used in conjunction with any complex queries.


## Complex Queries

Queries can be built by chaining multiple query parameters together.

```python
users_by_name = ref.child("users").orderBy("name").limitToFirst(3).get()
```
This query will return the first three users ordered by name.

#### orderBy

We begin any complex query with the orderBy parameter.

```python
users_by_name = ref.child("users").orderBy("name").get()
```
This query will return users ordered by name.

#### equalTo

Return data with a specific value.

```python
users_by_score = ref.child("users").orderBy("score").equalTo(10).get()
```
This query will return users with a score of 10.

#### startAt and endAt

Specify a range in your data.

```python
users_by_score = ref.child("users").orderBy("score").startAt(3).endAt(10).get()
```
This query returns users ordered by score and with a score between 3 and 10.

#### limitToFirst and limitToLast

Limits data returned.

```python
users_by_score = ref.child("users").orderBy("score").limitToFirst(5).get()
```
This query returns the first five users ordered by score.


## User Management

### Creating users

```python
ref.createUser("email", "password")
```
Note: Make sure you have Email & Password Authentication enabled on your firebase dashboard under Login & Auth.

### Removing users

```python
ref.removeUser("email", "password")
```

### Changing user passwords

```python
ref.changePassword("email", "old_password", "new_password")
```

### Sending password reset emails

```python
ref.sendPasswordResetEmail("email")
```

## Helper Methods

### generateKey

generateKey() is an implementation of Firebase's [key generation algorithm](https://www.firebase.com/blog/2015-02-11-firebase-unique-identifiers.html).

See multi-location updates for a potential use case.

### reSort

Sometimes we might want to sort our data multiple times. For example, we might want to retrieve all articles written between a
certain date then sort those articles based on the number of likes.

Currently the REST API only allows us to sort our data once, so the reSort() method bridges this gap.

```python
articles = ref.child("articles").orderBy("date").startAt(startDate).endAt(endDate).get()
articles_by_likes = reSort(articles, "likes")
```

## Common Errors

### Index not defined

Indexing is [not enabled](https://www.firebase.com/docs/security/guide/indexing-data.html) for the database reference.