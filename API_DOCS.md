# APP

## Version

Version 1 (currently in development).

For full instructions check the [`backend README`](./backend/README.md)

## API Documentation

### Application Endpoints

1. [GET /](#get-)
2. [POST /](#post-)
3. [POST /posts](#post-posts)
4. [PATCH /posts/<post_id>](#patch-postspost_id)
5. [DELETE /posts/<post_id>](#delete-postspost_id)
6. [GET /posts/<post_type>](#get-postspost_type)
7. [GET /users/<user_type>](#get-usersuser_type)
8. [GET /users/all/<user_id>](#get-usersalluser_id)
9. [POST /users](#post-users)
10. [PATCH /users/all/<user_id>](#patch-usersalluser_id)
11. [GET /users/all/<user_id>/posts](#get-usersalluser_idposts)
12. [DELETE /users/all/<user_id>/posts](#delete-usersalluser_idposts)
13. [GET /messages](#get-messages)
14. [POST /messages](#post-messages)
15. [DELETE /messages/<mailbox_type>/<item_id>](#delete-messagesmailbox_typeitem_id)
16. [DELETE /messages/<mailbox_type>](#delete-messagesmailbox_type)
17. [GET /reports](#get-reports)
18. [POST /reports](#post-reports)
19. [PATCH /reports/<report_id>](#patch-reportsreport_id)
20. [GET /filters](#get-filters)
21. [POST /filters](#post-filters)
22. [DELETE /filters/<filter_id>](#delete-filtersfilter_id)
23. [GET /notifications](#get-notifications)
24. [POST /notifications](#post-notifications)
25. [PATCH /notifications](#patch-notificationssub_id)

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

### POST /
**Description**: Runs a search in the posts and users' tables.

**Handler Function**: search.

**Request Arguments**:
  - page (Int) - An optional query parameter containing the current page of search results.

**Required Data**: A JSON containing a search query, in the following format:
  - search (string) - the search query.

**Required Permission:** None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - users (List) - List of users matching the query.
  - posts (List) - Paginated list of posts matching the query.
  - user_results (Number) - Total number of user results.
  - post_results (Number) - Total number of post results.
  - current_page (Number) - Current page of post results.
  - total_pages (Number) - Total pages of post results.

**Expected Errors**: None.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/ -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"search":"test"}'`

**Response Example:**
```
{
  "current_page": 1,
  "post_results": 7,
  "posts": [
    {
      "date": "Mon, 01 Jun 2020 15:20:11 GMT",
      "givenHugs": 0,
      "id": 7,
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
      "date": "Mon, 01 Jun 2020 15:18:37 GMT",
      "givenHugs": 0,
      "id": 5,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:17:56 GMT",
      "givenHugs": 0,
      "id": 4,
      "text": "test",
      "user": "shirb",
      "userId": 1
    },
    {
      "date": "Mon, 01 Jun 2020 15:15:12 GMT",
      "givenHugs": 0,
      "id": 3,
      "text": "testing",
      "user": "shirb",
      "userId": 1
    }
  ],
  "success": true,
  "total_pages": 2,
  "user_results": 0,
  "users": []
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

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/posts -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"user_id":4, "user":"user14", "text":"test curl", "date":"2020-06-07T15:57:45.901Z", "givenHugs":0}'`

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
  - 403 (Forbidden) - In case the user is attempting to edit the text of another user's posts without permission.
  - 404 (Not Found) - In case there's no post with that ID.
  - 500 (Internal Server Error) - In case there's an error updating the post's data in the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/posts/15 -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"user_id":4, "user":"user14", "text":"test curl", "date":"2020-06-07T15:57:45.901Z", "givenHugs":0}'`

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
  - 403 (Forbidden) - In case the user is attempting to edit the text of another user's posts without permission.
  - 404 (Not Found) - In case there's no post with that ID or there's no ID supplied.
  - 500 (Internal Server Error) - In case there's an error deleting the post from the database.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/posts/15 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "15",
  "success": true
}
```

### GET /posts/<post_type>
**Description**: Gets the new/recent posts, depending on the type passed on. Recent posts are ordered by descending order (most recent to least recent).

**Handler Function**: get_new_posts.

**Request Arguments**:
  - type (string) - The type of posts to fetch.
  - page (number) - An option query parameter indicating the current page.

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

### GET /users/<user_type>
**Description**: Gets a list of users by a given type (like 'blocked users') from the databsae.

**Handler Function**: get_users_by_type.

**Request Arguments**:
  - type (string) - The type of users to fetch from the database.
  - page (number) - An option query parameter indicating the current page.

**Required Data**: None.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - users (Dictionary) - A list containing the data of the users matching the given type.
  - total_pages (Number) - Total number of pages in the list.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/users/blocked -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "success": true,
  "total_pages": 0,
  "users": []
}
```

### GET /users/all/<user_id>
**Description**: Gets a user's data from the database.

**Handler Function**: get_user_data.

**Request Arguments**:
  - user_id - A parameter indicating the User's Firebase ID (This parameter comes directly from the user's JWT) or the user's ID (from the database).

**Required Data**: None.

**Required Permission:** 'read:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - User (Dictionary) - A dictionary containing the user's data.

**Expected Errors**:
  - 404 (Not Found) - In case no ID was supplied or there's no user with that ID.

**CURL Request Sample**: `curl http://127.0.0.1:5000/users/all/bc7e50 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "success": true,
  "user": {
    "auth0Id": "",
    "firebaseId": "bc7e50",
    "displayName": "user14",
    "givenH": 0,
    "id": 4,
    "loginCount": 5,
    "posts": 1,
    "receivedH": 0,
    "role": "admin",
  }
}
```

### POST /users
**Description**: Adds a new user to the database. This method is only used during the first login - it's only exposed to users within that initial session.

**Handler Function**: add_user.

**Request Arguments**: None.

**Required Data**: A JSON containing the new user's data, in the following format:
  - id (string) - The user's Firebase ID (JWT `uid` field).
  - displayName (string) - The user's auto-generated display name.

**Required Permission:** 'post:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - user (Dictionary) - The new user's data.

**Expected Errors**:
  - 409 (Conflict) - In case the user is attempting to create a user that already exists.
  - 422 (Unprocessable) - In case the user is attempting to create a user other than themselves.
  - 500 (Internal Server Error) - In case there's an error updating the user's data in the database.

### PATCH /users/all/<user_id>
**Description**: Updates a user's data in the database.

**Handler Function**: edit_user.

**Request Arguments**:
  - user_id - The ID of the user to update.

**Required Data**: A JSON containing the user's updated data, in the following format (all fields are optional):
  - receivedH (Number) - The user's received hugs.
  - givenH (Number) - The user's given hugs.
  - displayName (string) - The user's display name.
  - loginCount (Number) - The user's login count.
  - blocked (Boolean) - Whether or not the user is blocked.
  - releaseDate (Date) - When the user will be unblocked. Must be in request data if 'blocked' is set to true in the request data.

**Required Permission:** 'patch:user' or 'patch:any-user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - updated (Dictionary) - The updated user's data.

**Expected Errors**:
  - 403 (Forbidden) - In case the user is attempting to edit someone else's posts or block a user without the required permissions.
  - 404 (Not Found) - In case no ID was supplied.
  - 500 (Internal Server Error) - In case there's an error updating the user's data in the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/users/all/4 -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"displayName":"user_14", "receivedH":0, "givenH":0, "posts":2, "loginCount":2}'`

**Response Example:**
```
{
  "success": true,
  "updated": {
    "auth0Id": "c7e50",
    "displayName": "user_14",
    "givenH": 0,
    "id": 4,
    "loginCount": 2,
    "receivedH": 0,
    "role": "admin",
    "firebaseId": "fkfl"
  }
}
```

### GET /users/all/<user_id>/posts
**Description**: Gets the user's posts.

**Handler Function**: get_user_posts.

**Request Arguments**:
  - userID - The ID of the user.
  - page - An optional query parameter indicating the user's current page.

**Required Data**: None.

**Required Permission:** 'read:user'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - posts (List) - A paginated list of the user's posts (5 per request).
  - page (number) - The user's current page.
  - total_pages (number) - Total number of pages.

**Expected Errors**:
  - 400 (Bad Request) - In case there's no ID supplied.

**CURL Request Sample**: `curl http://127.0.0.1:5000/users/all/4/posts -H 'Authorization: Bearer <YOUR_TOKEN>'`

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

### DELETE /users/all/<user_id>/posts
**Description**: Deletes all of the user's posts.

**Handler Function**: delete_user_posts.

**Request Arguments**:
  - userID - The ID of the user.

**Required Data**: None.

**Required Permission:** 'delete:my-post' or 'delete:any-post'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - userID (number) - The user's ID.
  - deleted (number) - The number of deleted posts.

**Expected Errors**:
  - 403 (Forbidden) - In case the user is trying to delete another user's posts without the required permission.
  - 404 (Not Found) - In case there are no posts to delete.
  - 500 (Internal Server Error) - In case there's an issue deleting the posts.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/users/all/4/posts -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": 1,
  "success": true,
  "userID": "4"
}
```

### GET /messages
**Description**: Gets the user's messages.

**Handler Function**: get_user_messages.

**Request Arguments**:
  - userID - A query parameter indicating the User's ID.
  - page - An optional query parameter indicating the user's current page.
  - type - An optional query parameter indicating the type of messages the user is attempting to get (inbox, outbox, threads or a specific thread's messages).

**Required Data**: None.

**Required Permission:** 'read:messages'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - messages (List) - A paginated list containing the user's messages.
  - current_page (number) - The user's current page.
  - total_pages (number) - The total number of pages.

**Expected Errors**:
  - 400 (Bad Request) - In case no ID was supplied.
  - 403 (Forbidden) - In case the user is trying to read another user's messages.
  - 404 (Not Found) - In case the mailbox the user is requesting doesn't exist.

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
  - 403 (Forbidden) - In case the user is trying to post the message from another user.
  - 500 (Internal Server Error) - In case there's an error adding the new message (or the new thread if one is needed) to the database.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/messages -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"from":"user14", "fromId":4, "forId":1, "messageText":"hang in there", "date":"2020-06-07T15:57:45.901Z"}'`

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

### DELETE /messages/<mailbox_type>/<item_id>
**Description**: Deletes a message from the database.

**Handler Function**: delete_message.

**Request Arguments**:
  - mailbox_type - the type of mailbox from which to delete the message.
  - message_id - The ID of the message to delete.

**Required Data**: None.

**Required Permission:** 'delete:message'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (Number) - the ID of the message that was deleted.

**Expected Errors**:
  - 403 (Forbidden) - In case the user is trying to delete another user's message.
  - 404 (Not Found) - In case there's no message with that ID.
  - 405 (Method Not Allowed) - In case no ID was supplied.
  - 500 (Internal Server Error) - In case an error occurred while deleting the message from the database.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/messages/inbox/6 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "6",
  "success": true
}
```

### DELETE /messages/<mailbox_type>
**Description**: Clears the given mailbox (meaning, deletes all of the messages in it).

**Handler Function**: clear_mailbox.

**Request Arguments**:
  - mailbox_type - the type of mailbox from which to delete the messages.
  - userID - A query parameter indicating the User's ID.

**Required Data**: None.

**Required Permission:** 'delete:message'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - userID (number) - the ID of the user whose message were deleted.
  - deleted (Number) - the number of deleted messages.

**Expected Errors**:
  - 400 (Bad Request) - In case there's no mailbox type or user ID.
  - 403 (Forbidden) - In case the user is trying to delete another user's message.
  - 404 (Not Found) - In case there are no messages in the given mailbox.
  - 500 (Internal Server Error) - In case an error occurred while deleting the messages from the database.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/messages/inbox?userID=4 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "2",
  "success": true,
  "userID": "4"
}
```

### GET /reports
**Description**: Gets a paginated list of currently open user and post reports.

**Handler Function**: get_open_reports.

**Request Arguments**:
  - userPage - A query parameter indicating the current page of user reports.
  - postPage - A query parameter indicating the current page of post reports.

**Required Data**: None.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - userReports (List) - A list of paginated user reports.
  - totalUserPages (Number) - the total number of pages of user reports.
  - postReports (List) - A list of paginated post reports.
  - totalPostPages (Number) - the total number of pages of post reports.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/reports -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "postReports": [],
  "success": true,
  "totalPostPages": 0,
  "totalUserPages": 0,
  "userReports": []
}
```

### POST /reports
**Description**: Adds a new report to the database.

**Handler Function**: create_new_report.

**Request Arguments**: None.

**Required Data**: A JSON containing the report's data, in the following format:
  - type (string) - 'Post' or 'User', depending on the type of report being submitted.
  - userID (Number) - The ID of the user being reported.
  - postID (Number | null) - the ID of the post being reported (if any; for user reports this field is left empty).
  - reporter (Number) - The ID of the user making the report.
  - reportReason (String) - The reason for the report.
  - date (Date) - The date the report is submitted.

**Required Permission:** 'post:report'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - report (Dictionary) - the newly created report.

**Expected Errors**:
  - 404 (Not Found) - In case the item being reported doesn't exist.
  - 500 (Internal Server Error) - In case an error occurred while adding the new report to the database.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/reports -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"type":"Post", "userID":"1", "postID":4, "reporter":5,"reportReason":"this post is inappropriate", "date":"2020-06-07T15:57:45.901Z"}'`

**Response Example:**
```
{
  "report": {
    "closed": false,
    "date": "Tue Jun 23 2020 14:59:31 GMT+0300",
    "dismissed": false,
    "id": 36,
    "postID": 4,
    "reportReason": "this post is inappropriate",
    "reporter": 5,
    "type": "Post",
    "userID": "1"
  },
  "success": true
}
```

### PATCH /reports/<report_id>
**Description**: Updates a report's data (used to close an open report).

**Handler Function**: update_report_status.

**Request Arguments**:
  - report_id - the ID of the report to close.

**Required Data**: A JSON containing the updated report's data, in the following format:
  - type (string) - 'Post' or 'User', depending on the type of report being submitted.
  - userID (Number) - The ID of the user being reported.
  - postID (Number | null) - the ID of the post being reported (if any; for user reports this field is left empty).
  - reporter (Number) - The ID of the user making the report.
  - reportReason (String) - The reason for the report.
  - date (Date) - The date the report is submitted.
  - dismissed (Boolean) - Whether the report was dismissed.
  - closed (Boolean) - Whether the report was closed.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - report (Dictionary) - the newly created report.

**Expected Errors**:
  - 404 (Not Found) - In case a report with that ID doesn't exist.
  - 500 (Internal Server Error) - In case an error occurred while updating the report in the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/reports/36 -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"type":"Post", "userID":"1", "postID":4, "reporter":5,"reportReason":"this post is inappropriate", "date":"2020-06-07T15:57:45.901Z", "dismissed": true, "closed": true}'`

**Response Example:**
```
{
  "updated": {
    "closed": true,
    "date": "Tue Jun 23 2020 14:59:31 GMT+0300",
    "dismissed": true,
    "id": 36,
    "postID": 4,
    "reportReason": "this post is inappropriate",
    "reporter": 5,
    "type": "Post",
    "userID": "1"
  },
  "success": true
}
```

### GET /filters
**Description**: Gets a paginated list of filtered words.

**Handler Function**: get_filters.

**Request Arguments**:
  - page - A query parameter indicating the current page of filtered words.

**Required Data**: None.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - words (List) - A list of paginated filtered words.
  - total_pages (Number) - the total number of pages of filtered words.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/filters -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "success": true,
  "total_pages": 0,
  "words": []
}
```

### POST /filters
**Description**: Adds a new filtered word to the app.

**Handler Function**: add_filter.

**Request Arguments**: None.

**Required Data**: A JSON containing the new filter, in the following format:
  - word (string) - The filter.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - added (string) - the newly added filter.

**Expected Errors**:
  - 409 (Conflict) - In case the filter already exists.
  - 500 (Internal Server Error) - In case an error occurred while adding the new filter.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/filters -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '{"word":"sample"}'`

**Response Example:**
```
{
  "added": "sample",
  "success": true
}
```

### DELETE /filters/<filter_id>
**Description**: Deletes a word from the filters list (only possible for user-added words).

**Handler Function**: delete_filter.

**Request Arguments**:
  - filter_id (number) - the ID of the filter to delete (i.e., it's list index).

**Required Data**: None.

**Required Permission:** 'read:admin-board'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (string) - the deleted filter.

**Expected Errors**:
  - 404 (Not Found) - In case there's no filter in the given index.
  - 500 (Internal Server Error) - In case an error occurred while deleting the filter.

**CURL Request Sample**: `curl -X DELETE http://127.0.0.1:5000/filters/1 -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```
{
  "deleted": "sample",
  "success": true
}
```

### GET /notifications
**Description**: Gets the user's unread notifications

**Handler Function**: get_latest_notifications.

**Request Arguments**: None.

**Required Data**: None.

**Required Permission:** 'read:messages'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - notifications (List) - a list containing all user notifications

**Expected Errors**:
  - 404 (Not Found) - In case there's no user with the given Firebase ID.
  - 500 (Internal Server Error) - In case an error occurred while trying to update the user's 'last read' date.

**CURL Request Sample**: `curl http://127.0.0.1:5000/notifications -H 'Authorization: Bearer <YOUR_TOKEN>'`

**Response Example:**
```

```

### POST /notifications
**Description**: Adds a new PushSubscription to the subscriptions database.

**Handler Function**: add_notification_subscription.

**Request Arguments**: None.

**Required Data**: A PushSubscription data object, based on the Web Push Protocol. (For more information, check out [this link](https://www.w3.org/TR/push-api/#pushsubscription-interface)).

**Required Permission:** 'read:messages'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - subscribed (Number) - the display name of the newly subscribed user.
  - subId (Number) - the ID of the newly added push subscription.

**Expected Errors**:
  - 404 (Not Found) - In case there's no user with the given Firebase ID.
  - 500 (Internal Server Error) - In case an error occurred while trying to add the new subscription to the database.

**CURL Request Sample**: `curl -X POST http://127.0.0.1:5000/filters -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '<PUSH_SUBSCRIPTION_OBJECT>'`

**Response Example:**
```

```

### PATCH /notifications/<sub_id>
**Description**: Updates the details of a PushSubscription in the subscriptions table.

**Handler Function**: update_notification_subscription.

**Request Arguments**: None.

**Required Data**: A PushSubscription data object, based on the Web Push Protocol. (For more information, check out [this link](https://www.w3.org/TR/push-api/#pushsubscription-interface)).

**Required Permission:** 'read:messages'.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - subscribed (Number) - the display name of the newly subscribed user.
  - subId (Number) - the ID of the updated push subscription.

**Expected Errors**:
  - 404 (Not Found) - In case there's no user with the given Firebase ID.
  - 500 (Internal Server Error) - In case an error occurred while trying to add the new subscription to the database.

**CURL Request Sample**: `curl -X PATCH http://127.0.0.1:5000/notifications/sub_id -H "Content-Type: application/json" -H 'Authorization: Bearer <YOUR_TOKEN>' -d '<PUSH_SUBSCRIPTION_OBJECT>'`

**Response Example:**
```

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
