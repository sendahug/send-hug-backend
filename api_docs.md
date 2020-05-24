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
5. GET /users
6. POST /users
7. PATCH /users/<user_id>
8. GET /messages
9. POST /messages
10. DELETE /messages/<message_id>

### GET /
**Description**: Home route. Gets the ten most recent items and the ten items with the least hugs.

**Handler Function**: index.

**Request Arguments**: None.

**Required Data**: None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - Recent (Array) - An array of recent items.
  - Suggested (Array) - An array of suggested items.

**Expected Errors**: None.

**CURL Request Sample**: `curl http://127.0.0.1:5000/`

**Response Example:**
```
{

}
```

### POST /posts
**Description**: Creates a new post in the database.

**Handler Function**: add_post.

**Request Arguments**: None.

**Required Data**: A JSON containing a new post's data, in the following format:
  - userId (Number) - The ID of the user creating the post.
  - text (String) - The post text.
  - date (DateTime) - The date in which the post was made.
  - hugs (Number) - The post's given hugs.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - Posts (Dictionary) - the newly-added post.

**Expected Errors**:
  - 500 (Internal Server Error) - In case there's an error adding the new post to the database.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

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

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - updated (Dictionary) - the updated post.

**Expected Errors**:
  - 404 (Not Found) - In case there's no post with that ID.
  - 500 (Internal Server Error) - In case there's an error updating the post's data in the database.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### DELETE /posts/<post_id>
**Description**: Deletes a post from the database.

**Handler Function**: delete_post.

**Request Arguments**:
  - post_id - The ID of the post to delete.

**Required Data**: None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (Number) - The ID of the post deleted.

**Expected Errors**:
  - 404 (Not Found) - In case there's no post with that ID.
  - 500 (Internal Server Error) - In case there's an error deleting the post from the database.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### GET /users
**Description**: Gets a user's data from the database.

**Handler Function**: get_user_data.

**Request Arguments**:
  - userID - A query parameter indicating the User's Auth0 ID. This parameter comes directly from the user's JWT.

**Required Data**: None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - User (Dictionary) - A dictionary containing the user's data.

**Expected Errors**:
  - 404 (Not Found) - In case there's no ID supplied or there's no user with that ID.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### POST /users
**Description**: Adds a new user to the database. This method is only exposed to Auth0.

### PATCH /users/<user_id>
**Description**: Updates a user's data in the database.

**Handler Function**: edit_user.

**Request Arguments**:
  - user_id - The ID of the user to update.

**Required Data**: A JSON containing the post's updated data, in the following format:
  - receivedH (Number) - The user's received hugs.
  - givenH (Number) - The user's given hugs.
  - posts (Number) - Number of posts the user made.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - updated (Dictionary) - The updated user's data.

**Expected Errors**:
  - 500 (Internal Server Error) - In case there's an error updating the user's data in the database.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### GET /messages
**Description**: Gets the user's messages.

**Handler Function**: get_user_messages.

**Request Arguments**:
  - userID - A query parameter indicating the User's ID.

**Required Data**: None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - messages (List) - A list containing the user's messages.

**Expected Errors**:
  - 404 (Not Found) - In case there's no ID supplied.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

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

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - message (Dictionary) - a dictionary containing the newly-sent message.

**Expected Errors**:
  - 500 (Internal Server Error) - In case there's an error adding the new message to the database.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### DELETE /messages/<message_id>
**Description**: Deletes a message from the database.

**Handler Function**: delete_message,

**Request Arguments**:
  - message_id - The ID of the message to delete.

**Required Data**: None.

**Returns**: An object containing:
  - Success (Boolean) - a success value.
  - deleted (Number) - the ID of the message that was deleted.

**Expected Errors**:
  - 404 (Not Found) - In case there's no message with that ID.

**CURL Request Sample**: `curl `

**Response Example:**
```
{

}
```

### Error Handlers

The app contains the following error handlers:
1. 400 - Bad Request
2. 404 - Not Found
3. 422 - Unprocessable Entity
4. 500 - Internal Server Error

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
