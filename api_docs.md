# APP

## Version

Version 1 (currently in development).

For full instructions check the [`backend README`](./backend/README.md)

## API Documentation

### Application Endpoints

1. GET /
2. POST /posts
3. PATCH /posts/<post_id>
4. DELETE /posts/<post_id>
5. GET /posts/<type>
6. GET /users/<user_id>
7. POST /users
8. PATCH /users/<user_id>
9. GET /users/<user_id>/posts
10. GET /messages
11. POST /messages
12. DELETE /messages/<message_id>

**NOTE**: All sample curl requests are done via user 4; for your own tests, change the user ID and the user's display name.

### GET /
**Description**: Home route. Gets the ten most recent items and the ten items with the least hugs.

**Handler Function**: index.

**Request Arguments**: None.

**Required Data**: None.

**Required Permission:** None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - Recent (Array) - An array of recent items.
  - Suggested (Array) - An array of suggested items.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/`

**Response Example:**
```
{
  "recent": [
    {
      "date": "Mon, 08 Jun 2020 14:43:15 GMT",
      "givenHugs": 0,
      "id": 15,
      "text": "testing user 3",
      "user": "user14",
      "userId": 4
    },
    {
      "date": "Mon, 08 Jun 2020 14:43:05 GMT",
      "givenHugs": 0,
      "id": 14,
      "text": "new here",
      "user": "user14",
      "userId": 4
    },
    {
      "date": "Mon, 08 Jun 2020 14:30:58 GMT",
      "givenHugs": 0,
      "id": 13,
      "text": "2nd post",
      "user": "user52",
      "userId": 5
    },
    {
      "date": "Mon, 08 Jun 2020 14:07:25 GMT",
      "givenHugs": 0,
      "id": 12,
      "text": "new user",
      "user": "user52",
      "userId": 5
    },
    {
      "date": "Thu, 04 Jun 2020 08:15:50 GMT",
      "givenHugs": 1,
      "id": 11,
      "text": "baby lee :))",
      "user": "shirb",
      "userId": 1
    }
  ],
  "success": true,
  "suggested": [
    {
      "date": "Mon, 08 Jun 2020 14:43:15 GMT",
      "givenHugs": 0,
      "id": 15,
      "text": "testing user 3",
      "user": "user14",
      "userId": 4
    },
    {
      "date": "Mon, 01 Jun 2020 15:18:37 GMT",
      "givenHugs": 0,
      "id": 5,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:19:41 GMT",
      "givenHugs": 0,
      "id": 6,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:20:11 GMT",
      "givenHugs": 0,
      "id": 7,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 08 Jun 2020 14:30:58 GMT",
      "givenHugs": 0,
      "id": 13,
      "text": "2nd post",
      "user": "user52",
      "userId": 5
    }
  ]
}
```

### POST /posts
**Description**: Creates a new post in the database.

**Handler Function**: add_post.

**Request Arguments**: None.

**Required Data**: A JSON containing a new post's data, in the following format:
  - user_id (Number) - The ID of the user creating the post.
  - text (String) - The post text.
  - date (DateTime) - The date in which the post was made.
  - givenHugs (Number) - The post's given hugs.

**Required Permission:** 'post:post'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - Posts (Dictionary) - the newly-added post.

**Expected Errors**:
  - 500 (Internal Server Error) - In case there's an error adding the new post to the database.

**CURL Request Sample**: `  curl -X POST http://127.0.0.1:5000/posts -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"user_id":4, "user":"user14", "text":"test curl", "date":"Wed Jun 10 2020 10:30:05 GMT+0300", "givenHugs":0}'`

**Response Example:**
```
{
  "posts": {
    "date": "Wed Jun 10 2020 10:30:05 GMT+0300",
    "givenHugs": 0,
    "id": null,
    "text": "test curl",
    "userId": 4
  },
  "success": true
}
```

### PATCH /posts/<post_id>
**Description**: Updates a post's text or its given hugs.

**Handler Function**: edit_post.

**Request Arguments**:
  - post_id - The ID of the post to edit.

**Required Data**: A JSON containing the post's updated data, in the following format:
  - text (String) - The updated post's text.
  - given_hugs (Number) - The updated hugs count.

**Required Permission:** 'patch:my-post' or 'patch:any-post'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - updated (Dictionary) - the updated post.

**Expected Errors**:
  - 400 (Bad Request) - In case there was no ID supplied.
  - 404 (Not Found) - In case there's no post with that ID.
  - 500 (Internal Server Error) - In case there's an error updating the post's data in the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/posts/15 -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"user_id":4, "user":"user14", "text":"test curl", "date":"Wed Jun 10 2020 10:30:05 GMT+0300", "givenHugs":0}'`

**Response Example:**
```
{
  "success": true,
  "updated": {
    "date": "Mon, 08 Jun 2020 14:43:15 GMT",
    "givenHugs": 0,
    "id": 15,
    "text": "test curl",
    "userId": 4
  }
}
```

### DELETE /posts/<post_id>
**Description**: Deletes a post from the database.

**Handler Function**: delete_post.

**Request Arguments**:
  - post_id - The ID of the post to delete.

**Required Data**: None.

**Required Permission:** 'delete:my-post' or 'delete:any-post'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (Number) - The ID of the post deleted.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.
  - 404 (Not Found) - In case there's no post with that ID.
  - 500 (Internal Server Error) - In case there's an error deleting the post from the database.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/posts/15 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "15",
  "success": true
}
```

### GET /posts/<type>
**Description**: Gets the new/recent posts, depending on the type passed on. Recent posts are ordered by descending order (most recent to least recent).

**Handler Function**: get_new_posts.

**Request Arguments**:
  - type (string) - The type of posts to fetch.
  - page (number) - Current page.

**Required Data**: None.

**Required Permission:** None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - Posts (Array) - An array of paginated posts (5 per request).
  - total_pages (Number) - The number of total pages.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/posts/new` or `curl http://127.0.0.1:5000/posts/suggested`

**Response Example:**
1. For new posts:
```
{
  "posts": [
    {
      "date": "Mon, 08 Jun 2020 14:43:05 GMT",
      "givenHugs": 0,
      "id": 14,
      "text": "new here",
      "user": "user14",
      "userId": 4
    },
    {
      "date": "Mon, 08 Jun 2020 14:30:58 GMT",
      "givenHugs": 0,
      "id": 13,
      "text": "2nd post",
      "user": "user52",
      "userId": 5
    },
    {
      "date": "Mon, 08 Jun 2020 14:07:25 GMT",
      "givenHugs": 0,
      "id": 12,
      "text": "new user",
      "user": "user52",
      "userId": 5
    },
    {
      "date": "Thu, 04 Jun 2020 08:15:50 GMT",
      "givenHugs": 1,
      "id": 11,
      "text": "baby lee :))",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Thu, 04 Jun 2020 07:56:09 GMT",
      "givenHugs": 0,
      "id": 10,
      "text": "cutie baby lee",
      "user": "shirb",
      "userId": 1
    }
  ],
  "success": true,
  "total_pages": 3
}
```

2. For suggested posts:
```
{
  "posts": [
    {
      "date": "Mon, 08 Jun 2020 14:43:05 GMT",
      "givenHugs": 0,
      "id": 14,
      "text": "new here",
      "user": "user14",
      "userId": 4
    },
    {
      "date": "Mon, 01 Jun 2020 15:18:37 GMT",
      "givenHugs": 0,
      "id": 5,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:19:41 GMT",
      "givenHugs": 0,
      "id": 6,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:20:11 GMT",
      "givenHugs": 0,
      "id": 7,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 08 Jun 2020 14:07:25 GMT",
      "givenHugs": 0,
      "id": 12,
      "text": "new user",
      "user": "user52",
      "userId": 5
    }
  ],
  "success": true,
  "total_pages": 3
}
```

### GET /users/<user_id>
**Description**: Gets a user's data from the database.

**Handler Function**: get_user_data.

**Request Arguments**:
  - user_id - A parameter indicating the User's Auth0 ID. This parameter comes directly from the user's JWT.

**Required Data**: None.

**Required Permission:** 'read:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - User (Dictionary) - A dictionary containing the user's data.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.
  - 404 (Not Found) - In case there's no user with that ID.

**CURL Request Sample**: `curl http://127.0.0.1:5000/users/auth0%7C5ed8e3d0def75d0befbc7e50 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "success": true,
  "user": {
    "auth0Id": "auth0|5ed8e3d0def75d0befbc7e50",
    "displayName": "user14",
    "givenH": 0,
    "id": 4,
    "loginCount": 5,
    "posts": 1,
    "receivedH": 0,
    "role": "admin"
  }
}
```

### POST /users
**Description**: Adds a new user to the database. This method is only used during the first login - it's only exposed to users within that initial session.

**Handler Function**: add_user.

**Request Arguments**: None.

**Required Data**: A JSON containing the new user's data, in the following format:
  - id (string) - The user's Auth0 ID (JWT sub).
  - displayName (string) - The user's auto-generated display name.

**Required Permission:** 'post:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - user (Dictionary) - The new user's data.

**Expected Errors**:
  - 409 (Conflict) - In case the user is attempting to create a user that already exists.
  - 500 (Internal Server Error) - In case there's an error updating the user's data in the database.

### PATCH /users/<user_id>
**Description**: Updates a user's data in the database.

**Handler Function**: edit_user.

**Request Arguments**:
  - user_id - The ID of the user to update.

**Required Data**: A JSON containing the post's updated data, in the following format:
  - receivedH (Number) - The user's received hugs.
  - givenH (Number) - The user's given hugs.
  - posts (Number) - Number of posts the user made.

**Required Permission:** 'patch:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - updated (Dictionary) - The updated user's data.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.
  - 500 (Internal Server Error) - In case there's an error updating the user's data in the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/users/4 -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"displayName":"user_14", "receivedH":0, "givenH":0, "posts":2, "loginCount":2}'`

**Response Example:**
```
{
  "success": true,
  "updated": {
    "auth0Id": "auth0|5ed8e3d0def75d0befbc7e50",
    "displayName": "user_14",
    "givenH": 0,
    "id": 4,
    "loginCount": 2,
    "receivedH": 0,
    "role": "admin"
  }
}
```

### GET /users/<user_id>/posts
**Description**: Gets the user's posts.

**Handler Function**: get_user_posts.

**Request Arguments**:
  - userID - The ID of the user.
  - page - A query parameters indicating the user's current page.

**Required Data**: None.

**Required Permission:** 'read:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - posts (List) - A paginated list of the user's posts (5 per request).
  - page (number) - The user's current page.
  - total_pages (number) - Total number of pages.

**Expected Errors**:
  - 400 (Bad Request) - In case there's no ID supplied.

**CURL Request Sample**: `curl http://127.0.0.1:5000/users/4/posts -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "page": 1,
  "posts": [
    {
      "date": "Mon, 08 Jun 2020 14:43:05 GMT",
      "givenHugs": 0,
      "id": 14,
      "text": "new here",
      "userId": 4
    }
  ],
  "success": true,
  "total_pages": 1
}
```

### GET /messages
**Description**: Gets the user's messages.

**Handler Function**: get_user_messages.

**Request Arguments**:
  - userID - A query parameter indicating the User's ID.

**Required Data**: None.

**Required Permission:** 'read:messages'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - messages (List) - A paginated list containing the user's messages.
  - current_page (number) - The user's current page.
  - total_pages (number) - The total number of pages.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.

**CURL Request Sample**: `curl http://127.0.0.1:5000/messages?userID=4 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "current_page": 1,
  "messages": [
    {
      "date": "Mon, 08 Jun 2020 14:44:55 GMT",
      "for": "user_14",
      "forId": 4,
      "from": "shirb",
      "fromId": 1,
      "id": 6,
      "messageText": "hiiii"
    },
    {
      "date": "Mon, 08 Jun 2020 14:50:19 GMT",
      "for": "user_14",
      "forId": 4,
      "from": "user52",
      "fromId": 5,
      "id": 8,
      "messageText": "hi there :)"
    }
  ],
  "success": true,
  "total_pages": 1
}
```

### POST /messages
**Description**: Adds a new message to the database.

**Handler Function**: add_message.

**Request Arguments**: None.

**Required Data**: A JSON containing the new message, in the following format:
  - fromId (Number) - ID of the user sending the message.
  - forId (Number) - ID of the user getting the message.
  - text (String) - The message text.
  - date (DateTime) - The date the message was sent.

**Required Permission:** 'post:message'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - message (Dictionary) - a dictionary containing the newly-sent message.

**Expected Errors**:
  - 500 (Internal Server Error) - In case there's an error adding the new message to the database.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/messages -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"from":"user14", "fromId":4, "forId":1, "messageText":"hang in there", "date":"Mon, 08 Jun 2020 14:43:15 GMT"}'`

**Response Example:**
```
{
  "message": {
    "date": "Mon, 08 Jun 2020 14:43:15 GMT",
    "forId": 1,
    "fromId": 4,
    "id": 9,
    "messageText": "hang in there"
  },
  "success": true
}
```

### DELETE /messages/<message_id>
**Description**: Deletes a message from the database.

**Handler Function**: delete_message,

**Request Arguments**:
  - message_id - The ID of the message to delete.

**Required Data**: None.

**Required Permission:** 'delete:message'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (Number) - the ID of the message that was deleted.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.
  - 404 (Not Found) - In case there's no message with that ID.
  - 500 (Internal Server Error) - In case an error occurred while deleting the message from the database.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/messages/6 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "6",
  "success": true
}
```

### Error Handlers

The app contains the following error handlers:
1. 400 - Bad Request
2. 404 - Not Found
3. 405 - Method Not Allowed
4. 409 - Conflict
5. 422 - Unprocessable Entity
6. 500 - Internal Server Error
7. AuthError (401 & 403) - Authentication errors.

For all errors, the server returns the following object:
  - A success value ('success') - Boolean
  - The HTTP status code ('error') - Integer
  - An explanation message ('message') - String

Example:
```
{
  "error": 404,
  "message": "The resource you were looking for wasn\'t found.",
  "success": false
}
```

AuthError example:
```
{
  "code": 401,
  "message": {
    "code": 401,
    "description": "Unauthorised. Your token is invalid."
  },
  "success": false
}
```
