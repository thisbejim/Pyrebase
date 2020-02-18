# Pyrebase

A simple python wrapper for the [Firebase API](https://firebase.google.com).

## Support

Does your business or project depend on Pyrebase? Reach out to pibals@protonmail.com

## Installation

```python
pip install pyrebase
```

## Getting Started

### Python Version

Pyrebase was written for python 3 and will not work correctly with python 2.

### Add Pyrebase to your application

For use with only user based authentication we can create the following configuration:

```python
import pyrebase

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "projectId.appspot.com"
}

firebase = pyrebase.initialize_app(config)
```

We can optionally add a [service account credential](https://firebase.google.com/docs/server/setup#prerequisites) to our
configuration that will allow our server to authenticate with Firebase as an admin and disregard any security rules.

```python
import pyrebase

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "projectId.appspot.com",
  "serviceAccount": "path/to/serviceAccountCredentials.json"
}

firebase = pyrebase.initialize_app(config)
```

Adding a service account will authenticate as an admin by default for all database queries, check out the
[Authentication documentation](#authentication) for how to authenticate users.

### Use Services

A Pyrebase app can use multiple Firebase services.

```firebase.auth()``` - [Authentication](#authentication)

```firebase.database()``` - [Database](#database)

```firebase.storage()``` - [Storage](#storage)

Check out the documentation for each service for further details.

## Authentication

The ```sign_in_with_email_and_password()``` method will return user data including a token you can use to adhere to security rules.

Each of the following methods accepts a user token: ```get()```, ```push()```, ```set()```, ```update()```, ```remove()``` and ```stream()```.

```python
# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(email, password)

# Get a reference to the database service
db = firebase.database()

# data to save
data = {
    "name": "Mortimer 'Morty' Smith"
}

# Pass the user's idToken to the push method
results = db.child("users").push(data, user['idToken'])
```

### Token expiry

A user's idToken expires after 1 hour, so be sure to use the user's refreshToken to avoid stale tokens.
```
user = auth.sign_in_with_email_and_password(email, password)
# before the 1 hour expiry:
user = auth.refresh(user['refreshToken'])
# now we have a fresh token
user['idToken']
```

### Custom tokens

You can also create users using [custom tokens](https://firebase.google.com/docs/auth/server/create-custom-tokens), for example:
```
token = auth.create_custom_token("your_custom_id")
```
You can also pass in additional claims.
```
token_with_additional_claims = auth.create_custom_token("your_custom_id", {"premium_account": True})
```
You can then send these tokens to the client to sign in, or sign in as the user on the server.
```
user = auth.sign_in_with_custom_token(token)
```

### Manage Users

#### Creating users

```python
auth.create_user_with_email_and_password(email, password)
```
Note: Make sure you have the Email/password provider enabled in your Firebase dashboard under Auth -> Sign In Method.

#### Verifying emails

```python
auth.send_email_verification(user['idToken'])
```

#### Sending password reset emails

```python
auth.send_password_reset_email("email")
```

#### Get account information
```python
auth.get_account_info(user['idToken'])
```

#### Refreshing tokens
```python
user = auth.refresh(user['refreshToken'])
```

## Database

You can build paths to your data by using the ```child()``` method.

```python
db = firebase.database()
db.child("users").child("Morty")
```

### Save Data

#### push

To save data with a unique, auto-generated, timestamp-based key, use the ```push()``` method.

```python
data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").push(data)
```

#### set

To create your own keys use the ```set()``` method. The key in the example below is "Morty".

```python
data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").child("Morty").set(data)
```

#### update

To update data for an existing entry use the ```update()``` method.

```python
db.child("users").child("Morty").update({"name": "Mortiest Morty"})
```

#### remove

To delete data for an existing entry use the ```remove()``` method.

```python
db.child("users").child("Morty").remove()
```

#### multi-location updates

You can also perform [multi-location updates](https://www.firebase.com/blog/2015-09-24-atomic-writes-and-more.html) with the ```update()``` method.

```python
data = {
    "users/Morty/": {
        "name": "Mortimer 'Morty' Smith"
    },
    "users/Rick/": {
        "name": "Rick Sanchez"
    }
}

db.update(data)
```

To perform multi-location writes to new locations we can use the ```generate_key()``` method.

```python
data = {
    "users/"+ref.generate_key(): {
        "name": "Mortimer 'Morty' Smith"
    },
    "users/"+ref.generate_key(): {
        "name": "Rick Sanchez"
    }
}

db.update(data)
```

### Retrieve Data

#### val
Queries return a PyreResponse object. Calling ```val()``` on these objects returns the query data.

```
users = db.child("users").get()
print(users.val()) # {"Morty": {"name": "Mortimer 'Morty' Smith"}, "Rick": {"name": "Rick Sanchez"}}
```

#### key
Calling ```key()``` returns the key for the query data.

```
user = db.child("users").get()
print(user.key()) # users
```

#### each
Returns a list of objects on each of which you can call ```val()``` and ```key()```.

```
all_users = db.child("users").get()
for user in all_users.each():
    print(user.key()) # Morty
    print(user.val()) # {name": "Mortimer 'Morty' Smith"}
```

#### get

To return data from a path simply call the ```get()``` method.

```python
all_users = db.child("users").get()
```

#### shallow

To return just the keys at a particular path use the ```shallow()``` method.

```python
all_user_ids = db.child("users").shallow().get()
```

Note: ```shallow()``` can not be used in conjunction with any complex queries.

#### streaming

You can listen to live changes to your data with the ```stream()``` method.

```python
def stream_handler(message):
    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

my_stream = db.child("posts").stream(stream_handler)
```

You should at least handle `put` and `patch` events. Refer to ["Streaming from the REST API"][streaming] for details.

[streaming]: https://firebase.google.com/docs/reference/rest/database/#section-streaming

You can also add a ```stream_id``` to help you identify a stream if you have multiple running:

```
my_stream = db.child("posts").stream(stream_handler, stream_id="new_posts")
```

#### close the stream

```python
my_stream.close()
```

### Complex Queries

Queries can be built by chaining multiple query parameters together.

```python
users_by_name = db.child("users").order_by_child("name").limit_to_first(3).get()
```
This query will return the first three users ordered by name.

#### order_by_child

We begin any complex query with ```order_by_child()```.

```python
users_by_name = db.child("users").order_by_child("name").get()
```
This query will return users ordered by name.

#### equal_to

Return data with a specific value.

```python
users_by_score = db.child("users").order_by_child("score").equal_to(10).get()
```
This query will return users with a score of 10.

#### start_at and end_at

Specify a range in your data.

```python
users_by_score = db.child("users").order_by_child("score").start_at(3).end_at(10).get()
```
This query returns users ordered by score and with a score between 3 and 10.

#### limit_to_first and limit_to_last

Limits data returned.

```python
users_by_score = db.child("users").order_by_child("score").limit_to_first(5).get()
```
This query returns the first five users ordered by score.

#### order_by_key

When using ```order_by_key()``` to sort your data, data is returned in ascending order by key.

```python
users_by_key = db.child("users").order_by_key().get()
```

#### order_by_value

When using ```order_by_value()```, children are ordered by their value.

```python
users_by_value = db.child("users").order_by_value().get()
```


## Storage

The storage service allows you to upload images to Firebase.

### child

Just like with the Database service, you can build paths to your data with the Storage service.

```python
storage.child("images/example.jpg")
```

### put

The put method takes the path to the local file and an optional user token.

```python
storage = firebase.storage()
# as admin
storage.child("images/example.jpg").put("example2.jpg")
# as user
storage.child("images/example.jpg").put("example2.jpg", user['idToken'])
```

### download

The download method takes the path to the saved database file and the name you want the downloaded file to have.

```
storage.child("images/example.jpg").download("downloaded.jpg")
```

### get_url

The get_url method takes the path to the saved database file and returns the storage url.

```
storage.child("images/example.jpg").get_url()
# https://firebasestorage.googleapis.com/v0/b/storage-url.appspot.com/o/images%2Fexample.jpg?alt=media
```

### Helper Methods

#### generate_key

```db.generate_key()``` is an implementation of Firebase's [key generation algorithm](https://www.firebase.com/blog/2015-02-11-firebase-unique-identifiers.html).

See multi-location updates for a potential use case.

#### sort

Sometimes we might want to sort our data multiple times. For example, we might want to retrieve all articles written between a
certain date then sort those articles based on the number of likes.

Currently the REST API only allows us to sort our data once, so the ```sort()``` method bridges this gap.

```python
articles = db.child("articles").order_by_child("date").start_at(startDate).end_at(endDate).get()
articles_by_likes = db.sort(articles, "likes")
```

### Common Errors

#### Index not defined

Indexing is [not enabled](https://www.firebase.com/docs/security/guide/indexing-data.html) for the database reference.
