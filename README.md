# Pyrebase [![](https://img.shields.io/pypi/v/Pyrebase.svg)](https://pypi.python.org/pypi/Pyrebase) [![](https://img.shields.io/pypi/dm/Pyrebase.svg)](https://pypi.python.org/pypi/Pyrebase)

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

When initialising your Firebase you can also pass in a timestamp to specify when the admin token should expire:

```
jan_2100 = 4102444800
ref = pyrebase.Firebase('https://yourfirebaseurl.firebaseio.com', 'yourfirebasesecret', jan_2100)
```

### User authentication

The ```auth_with_password()``` method will return user data including a token you can use to adhere to security rules.

Each of the following methods accepts an optional user token: ```get()```, ```push()```, ```set()```, ```update()```, ```remove()``` and ```stream()```.

```python
user = ref.auth_with_password("email", "password")
data = {
    "date": "26-10-1985"
}
results = ref.child("users").child("Marty").update(data, user["token"])
```

## Building Paths
You can build paths to your data by using the ```child()``` method.

```python
ref.child("users").child("Marty")
```

## Saving Data

#### push

To save data with a unique, auto-generated, timestamp-based key, use the ```push()``` method.

```python
data = {"name": "Marty Mcfly", "date": "05-11-1955"}
ref.child("users").push(data)
```

#### set

To create your own keys use the ```set()``` method. The key in the example below is "Marty".

```python
data = {"Marty": {"name": "Marty Mcfly", "date":"05-11-1955"}}
ref.child("users").set(data)
```

#### update

To update data for an existing entry use the ```update()``` method.

```python
ref.child("users").child("Marty").update({"date": "26-10-1985"})
```

#### remove

To delete data for an existing entry use the ```remove()``` method.

```python
ref.child("users").child("Marty").remove()
```

### Multi-location updates

You can also perform [multi-location updates](https://www.firebase.com/blog/2015-09-24-atomic-writes-and-more.html) with the ```update()``` method.

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

To perform multi-location writes to new locations we can use the ```generate_key()``` method.

```python
data = {
    "users/"+ref.generate_key(): {
        "date": "26-10-1985"
    },
    "users/"+ref.generate_key(): {
        "date": "26-10-1985"
    }
}

ref.update(data)
```

## Queries

### val
Queries return a PyreResponse object. Calling ```val()``` on these objects returns the query data.

```
users = ref.child("users").get()
print(users.val()) # {"Marty": {"name": "Marty", "date": "26-10-1985"}, "Doc": {"name": "Doc", "date": "01-01-1885"}}
```

### key
Calling ```key()``` returns the key for the query data.

```
user = ref.child("users").get()
print(user.key()) # users
```

### each
Returns a list of objects on each of which you can call ```val()``` and ```key()```.

```
all_users = ref.child("users").get()
for user in all_users.each():
    print(user.key()) # Marty
    print(user.val()) # {name": "Marty", "date": "26-10-1985"}
```

#### get

To return data from a path simply call the ```get()``` method.

```python
all_users = ref.child("users").get()
```

#### shallow

To return just the keys at a particular path use the ```shallow()``` method.

```python
all_user_ids = ref.child("users").shallow().get()
```

Note: ```shallow()``` can not be used in conjunction with any complex queries.

## Streaming

You can listen to live changes to your data with the ```stream()``` method.

```python
def stream_handler(post):
    print(post["event"]) # put
    print(post["path"]) # /-K7yGTTEp7O549EzTYtI
    print(post["data"]) # {'title': 'Pyrebase', "body": "etc..."}

my_stream = ref.child("posts").stream(stream_handler)
```

#### close the stream

```python
my_stream.close()
```

## Complex Queries

Queries can be built by chaining multiple query parameters together.

```python
users_by_name = ref.child("users").order_by_child("name").limit_to_first(3).get()
```
This query will return the first three users ordered by name.

#### order_by_child

We begin any complex query with ```order_by_child()```.

```python
users_by_name = ref.child("users").order_by_child("name").get()
```
This query will return users ordered by name.

#### equal_to

Return data with a specific value.

```python
users_by_score = ref.child("users").order_by_child("score").equal_to(10).get()
```
This query will return users with a score of 10.

#### start_at and end_at

Specify a range in your data.

```python
users_by_score = ref.child("users").order_by_child("score").start_at(3).end_at(10).get()
```
This query returns users ordered by score and with a score between 3 and 10.

#### limit_to_first and limit_to_last

Limits data returned.

```python
users_by_score = ref.child("users").order_by_child("score").limit_to_first(5).get()
```
This query returns the first five users ordered by score.


## User Management

### Creating users

```python
ref.create_user("email", "password")
```
Note: Make sure you have Email & Password Authentication enabled on your firebase dashboard under Login & Auth.

### Removing users

```python
ref.remove_user("email", "password")
```

### Changing user passwords

```python
ref.change_password("email", "old_password", "new_password")
```

### Sending password reset emails

```python
ref.send_password_reset_email("email")
```

## Helper Methods

### generate_key

```generate_key()``` is an implementation of Firebase's [key generation algorithm](https://www.firebase.com/blog/2015-02-11-firebase-unique-identifiers.html).

See multi-location updates for a potential use case.

### sort

Sometimes we might want to sort our data multiple times. For example, we might want to retrieve all articles written between a
certain date then sort those articles based on the number of likes.

Currently the REST API only allows us to sort our data once, so the ```sort()``` method bridges this gap.

```python
articles = ref.child("articles").order_by_child("date").start_at(startDate).end_at(endDate).get()
articles_by_likes = ref.sort(articles, "likes")
```

## Common Errors

### Index not defined

Indexing is [not enabled](https://www.firebase.com/docs/security/guide/indexing-data.html) for the database reference.
