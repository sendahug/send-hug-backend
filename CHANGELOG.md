# Changelog

## Unreleased

### 2024-04-28

#### Features

- Added a logger to the Database Handler class and added logging for all errors raised by the database. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))

#### Changes

- Updated all database interactions to use SQLAlchemy's asyncio extension. The engine, session maker and session have been replaced by their async variants, and the helper methods for interacting with the database have all been updated to use async/await. This means that we can now write asynchronous code for read, write, update and delete, which should allow the server itself to handle more requests at once. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))
- The helper methods for creating and updating objects now return the formatted object instead of the raw SQLAlchemy object. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))
- Changed several relationships (user relationship in posts; role relationship in users; and permission relationship in roles) to use eager loading using 'selectin' instead of the default lazy loading. The SQLAlchemy asyncio extension doesn't support accessing attributes of lazily-loaded objects, and all three attributes are required to return the formatted versions of the models they're defined in (post, user and role respectively). ([#618](https://github.com/sendahug/send-hug-backend/pull/618))
- Changed the name of the Quart app from the current file's name to `SendAHug` to better reflect the server's purpose. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))

#### Fixes

- Dates are now explicitly parsed from strings passed into the API (using `strptime`) and strings that contain integers (e.g., IDs) are explicitly cast from strings to integers. This fixes an issue where inserts and queries errored due to the wrong type being used for dates/IDs. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))
- Fixed a bug where an attempt to update user details (such as login count) returned a 403 error saying 'you don't have permission to block users'. This happened due to a recent change in the front-end, which now sends the whole user object (of the logged in user) back to the back-end on update (instead of just the updated fields). As the back-end was checking whether the 'blocked' field existed, instead of whether it changed, this caused that error to be raised. Now, the back-end checks whether the value of 'blocked' changed instead. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))

#### Chores

- Replaced psycopg2 with asyncpg as the driver used for database interactions, as psycopg2 doesn't support async/await. ([#618](https://github.com/sendahug/send-hug-backend/pull/618))

### 2024-04-27

#### Changes

- Replaced Flask with Quart as the primary framework powering the back-end. This includes:

#### Chores

- Added pytest-asyncio and updated all tests to use the async/await pattern as well (since the test client's HTTP-based methods and the request's data both return a coroutine). ([#615](https://github.com/sendahug/send-hug-backend/pull/615))
- Changed the way the database is reset between tests. Previously, we created a database dump file that was restored between tests. This was over-complicated and unscalable. Now, we populate the database once, before tests start; in order to ensure the database returns to its original state between tests, tests are run within a nested session, which is then rolled back between tests. ([#619](https://github.com/sendahug/send-hug-backend/pull/619))

### 2024-04-25

#### Changes

- The blocking and unblocking process for users now changes the user's role to a 'blocked user'/'user' when blocking/unblocking (respectively) users. This means we can use the regular authorisation check in the POST '/posts' endpoint instead of adding an extra check for whether a user is blocked. ([#614](https://github.com/sendahug/send-hug-backend/pull/614))

### 2024-04-23

#### Features

- Added a new configuration class to handle all the app's config and the setup of the database. ([#611](https://github.com/sendahug/send-hug-backend/pull/611))
- Added a new Database Controller class, which is responsible for setting up the database and the sessions for interacting with it, as well as performing the various CRUD operations the app performs. ([#611](https://github.com/sendahug/send-hug-backend/pull/611))

#### Changes

- Replaced Flask-Migrate with pure Alembic (which Flask-Migrate uses under the hood to handle database migrations). ([#611](https://github.com/sendahug/send-hug-backend/pull/611))
- Replaced Flask-SQLAlchemy with pure SQLAlchemy. The models now use a new `BaseModel` class as the declarative base (as per SQLAlchemy guidelines), and the helper functions previously provided by Flask-SQLAlchemy (e.g., paginate) have been replaced with the new implementations in the database controller. The syntax of all queries has been updated appropriately. ([#611](https://github.com/sendahug/send-hug-backend/pull/611))
- Moved all the helper methods from `db_helpers` to the new database controller class, as it makes more sense to keep all generic database functionality in one place. ([#611](https://github.com/sendahug/send-hug-backend/pull/611))
- Bulk edit/delete operations (e.g., delete all posts, set all messages to 'deleted' by user) now use the SQLAlchemy constructs for building DELETE/UPDATE statements. Previously, they were handled on a row-by-row basis, which was extremely inefficient. Now, they're grouped together into single (or a couple of) statements, which simplifies the process and properly uses the database's abilities to handle bulk actions. ([#611](https://github.com/sendahug/send-hug-backend/pull/611))
- All hug-related columns (sent/received hugs in users and posts) are now non-nullable (which they shouldn't have been in the first place). ([#611](https://github.com/sendahug/send-hug-backend/pull/611))

### 2024-04-19

#### Chores

- Upgraded the minimum Python version for running the app to Python 3.11. This includes updating the version in CI and in the README, as well as updating the type hints to match the 3.10+ style. ([#610](https://github.com/sendahug/send-hug-backend/pull/610))

### 2024-04-18

#### Changes

- Moved all endpoint-specific code from the database helpers to the relevant endpoints. The database helpers should be generic and simply commit to the database, handle errors and close the current session, but previously they also dealt with model-specific actions (e.g., deleting messages, posts and threads). Now, the model/endpoint-specific code was moved to the relevant endpoints, and the database helpers only include the code for communicating with the database, handling errors raised by it, and closing the session once the update is done. ([#609](https://github.com/sendahug/send-hug-backend/pull/609))
- Replaced the `delete_all` helper function with a function for bulk updating and deleting. While the old function required a delete target and the ID of the user whose items to should be deleted, the new function simple requires a list of `delete` statements to run and a list of objects that were updated and should be committed to the database. This allows us to perform multiple deletes and updates within the same session, and moves the responsibility for updating/deleting to the endpoint. ([#609](https://github.com/sendahug/send-hug-backend/pull/609))

### 2024-04-15

#### Fixes

- Added several missing security-related headers to all responses made by the server (as per OWASP best practices). ([#607](https://github.com/sendahug/send-hug-backend/pull/607))

### 2024-04-13

#### Changes

- Deleted the report update from 'edit user' and 'edit post' endpoints. Including the extra complication of updating reports in unrelated endpoints was bad practice. Each endpoint should be specific to its purpose. Now, in order to close reports, users need to make a request to the 'edit report' endpoint, as it should've been in the first place. ([#606](https://github.com/sendahug/send-hug-backend/pull/606))

### 2024-04-12

#### Features

- Added roles and permissions tables to the database, as well as a mapping table between roles and permissions. ([#605](https://github.com/sendahug/send-hug-backend/pull/605))

#### Changes

- Updated the user table to include a role_id foreign key. The user's role was adjusted to include the full details of the role (name, ID and permissions) instead of just the name of the role. ([#605](https://github.com/sendahug/send-hug-backend/pull/605))

#### Breaking Changes

- The authorisation process has been rewritten to use the new roles and permissions system. This includes:
	- The `requires_auth` decorator now fetches the currently-logged in user and checks the required permissions against the user's permissions in our database in all endpoints except for the create user endpoint (as the user doesn't exist yet).
	- The old process for updating a new user's role from NewUser to User was deleted. Since the only endpoint that checks the Auth0 permissions is the 'create users' endpoint, it doesn't really matter if we update the user's role in Auth0 or not; the role is checked internally in the API anyway.
	- All endpoints that previously fetched the currently logged in user for authorisation (i.e., messaging endpoints checking the user isn't attempting to access someone else's messages) now use the user data returned by the `required_auth` decorator.
	- The 'update user' endpoint no longer checks the Auth0 payload for permissions in order to update the users' role. A user's role is assigned in registration instead. ([#605](https://github.com/sendahug/send-hug-backend/pull/605))

### 2024-04-10

#### Chores

- Updated the copyright notices to include 2024. ([#604](https://github.com/sendahug/send-hug-backend/pull/604))

### 2024-04-06

#### Chores

- Adjusted the way the tests' database dump was generated. Previously, if changes were made to the database, the person making the changes had to update the file containing the database dump by manually running `pg_dump` locally. This made updating test data a complicated and sometimes frustrating process. That file has been replaced with a Python file, which contains SQLAlchemy model instances (one for each row in the database). In the beginning of the test suite's run, the database is populated with that file, and the updated database is dumped to a local file so it can be used to restore the database between tests. This makes it easier to update the test database, as all that anyone making a change needs to do is simply update the Python models. ([#601](https://github.com/sendahug/send-hug-backend/pull/601))

### 2024-04-05

#### Changes

- Converted the posts' `sent_hugs` column from a string column to an array column. This ensures we don't need to manually split the array when pulling data from the database and to join the array back into a string when pushing data to the database. ([#600](https://github.com/sendahug/send-hug-backend/pull/600))

#### Fixes

- Added a missing check in the users' update endpoint to ensure users aren't setting the refresh rate to a too-low rate that crashes the API (due to too many requests). ([#599](https://github.com/sendahug/send-hug-backend/pull/599))
- Fixed a bug where the `sent_hugs` array returned by the back-end was a list of strings, instead of a list of integers (due to us having to manually split the string saved in the database). ([#600](https://github.com/sendahug/send-hug-backend/pull/600))

#### Chores

- Updated the version of the Codecov orb we use in CI to the latest version. ([#597](https://github.com/sendahug/send-hug-backend/pull/597))
- Updated the way caching works in the Circle CI workflow. Previously, the cache and restore operations used a specific key made of the branch name and the package-lock's checksum. This meant that since it was specific to each branch, we were hardly ever using the cache we built. Instead, we just kept adding to it. This update ensures we actually use the cache, which should also lower the cache-storing costs. ([#597](https://github.com/sendahug/send-hug-backend/pull/597))

### 2024-04-03

#### Chores

- Automated the process of updating the changelog file when commits are merged to dev. This allows us to insert the date at the same time as the change, and ensures that we don't get repeated merge conflicts (due to different pull requests updating the changelog file). ([#594](https://github.com/sendahug/send-hug-backend/pull/594))
- Updated the instructions for updating the changelog file to reflect the new automated process. ([#594](https://github.com/sendahug/send-hug-backend/pull/594))

### 2024-04-02

#### Fixes

- Fixed a bug where users couldn't delete messages from the thread view because there was no handling for deleting messages from threads in the DELETE /messages endpoint ([#596](https://github.com/sendahug/send-hug-backend/pull/596)).

### 2024-04-01

#### Changes

- Updated the syntax of all `select` queries for SQLAlchemy 2. Previously, we were using SQLAlchemy 1's `Query` API, which is now deprecated. Now, we use `session.scalar` and `session.scalars` for selecting single and multiple items (respectively). ([#595](https://github.com/sendahug/send-hug-backend/pull/595))
- Updated the syntax of all paginated queries to the updated Flask-SQLAlchemy 3 / SQLAlchemy 2 syntax. Previously, we were using `Model.query.paginate()`. This has now been replaced by `db.paginate` ([#595](https://github.com/sendahug/send-hug-backend/pull/595)).
- The helper method for bulk deleting items (posts/messages/threads) now uses SQLAlchemy's delete method instead of the old query().delete() method, which is cleaner and faster than deleting items manually via the ORM ([#595](https://github.com/sendahug/send-hug-backend/pull/595)).
- The helper method for bulk updating items now only commits the session once. Previously, it was doing it for every object, but this is unnecessary and wastes time and resources. Now, the session is committed once all objects are updated (in the relevant endpoint), and we only loop over the updated objects to format them and return the JSON data ([#595](https://github.com/sendahug/send-hug-backend/pull/595)).

### 2024-03-31

#### Features

- Added type hints to all SQLAlchemy models ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).

#### Changes

- Replaced all queries that relied on selecting columns from different tables at the same time with single-model queries. The columns needed from other tables (e.g., the user-related columns in the messages' query) have been included in the SQLAlchemy model as `column_properties` instead. This means that we provide the SQL query for getting the relevant values, and SQLAlchemy executes it as part of our select statement. This is mostly an internal change that should have no impact whatsoever on the user, as the API's outputs should still remain the same ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).
- All models' `format` methods have been simplified and only refer to the provided model itself, without any need for external parameters ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).
- The joined queries, which used `db.session` for querying, where updated to use the relevant models' `query` method instead ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).
- Updated the fetches for the currently logged-in user to return a 404 error if the user doesn't exist instead of returning None (which then broke the rest of the relevant workflows). ([#593](https://github.com/sendahug/send-hug-backend/pull/593))

#### Fixes

- Replaced the deprecated `backref` parameter in the SQLAlchemy relationship definitions with the current `back_populates` parameter ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).
- Several SQLAlchemy queries were incorrectly using Python operators (or, and) as part of their `WHERE` clause instead of the bitwise operators or the dedicated SQLAlchemy methods. This meant that in some instances the second part of a query's filter was ignored. Now, all queries use the correct SQLAlchemy helper methods (`or_`, `and_`) for filtering ([#593](https://github.com/sendahug/send-hug-backend/pull/593)).

### 2024-03-30

#### Chores

- Deleted the unnecessary heading section from the pull request template ([#592](https://github.com/sendahug/send-hug-backend/pull/592)).

### 2024-03-29

#### Chores

- Added a changelog and instructions for writing changelog entries ([#585](https://github.com/sendahug/send-hug-backend/pull/585)).

### 2024-03-25

#### Chores

- Replaced the "update superproject repo" and "add to project" workflows to use the new reusable workflows defined in [sendahug/send-a-workflow](https://github.com/sendahug/send-a-workflow) ([#588](https://github.com/sendahug/send-hug-backend/pull/588)).

### 2024-03-08

#### Documentation

- Updated the main README's file list, testing instructions and deployment instructions ([#578](https://github.com/sendahug/send-hug-backend/pull/578)).

### 2024-03-07

#### Chores

- Cleaned up the requirements files. We don't need to keep a full list of everything that's being installed anymore (now that we're not deploying on Heroku), so there's no need to keep all the dependencies' dependencies in the requirements file. ([#577](https://github.com/sendahug/send-hug-backend/pull/577))

### 2024-03-05

#### Chores

- Added the GitHub Actions dependencies to dependabot to allow auto-updating Actions ([#569](https://github.com/sendahug/send-hug-backend/pull/569)).
- Added a workflow for adding new issues and pull requests to the primary project and a workflow for auto-labelling pull requests ([#575](https://github.com/sendahug/send-hug-backend/pull/575)).

### 2024-03-04

#### Chores

- Changed CircleCI to run tests only against PRs in the UI. This meant the CI workflow's code was adjusted to remove the branch restriction and the GitHub Actions workflow for triggering CI was disabled ([#570](https://github.com/sendahug/send-hug-backend/pull/570)).

### 2024-02-16

#### Chores

- Updated the version of Postgres in CI to v14 ([e374330](https://github.com/sendahug/send-hug-backend/commit/e374330272ea1b1a1c5a1c6e5992ce6150da0bf1)).

### 2023-10-29

#### Chores

- Updated werkzeug and Flask to v3 ([#504](https://github.com/sendahug/send-hug-backend/pull/504)).

### 2023-04-15

#### Chores

- Removed the codecov package from dev requirements as the package has been removed from pypi ([2e965de](https://github.com/sendahug/send-hug-backend/commit/2e965de87513c2b5b2b4b87f475d8c32ed8f6ebc)).

### 2023-04-09

#### Chores

- Replaced the codecov package in CI with the official CircleCI codecov orb ([a7b7014](https://github.com/sendahug/send-hug-backend/commit/a7b7014938007170e86ed0d2f6601792c66c215c)).

### 2023-03-05

#### Features

- Added two new endpoints for sending hugs, one for sending hugs to users and one for sending hugs for posts ([d936848](https://github.com/sendahug/send-hug-backend/commit/d936848c1a8fb3f4b9b92d1ff65352b1a6e4ff9c) - [0354c21](https://github.com/sendahug/send-hug-backend/commit/0354c21b8bbcae9cd51d826f8078b2d00ad2ff88)).

#### Changes

- Moved all hugs-handling from the post and user edit endpoints to the new hugs endpoints ([d936848](https://github.com/sendahug/send-hug-backend/commit/d936848c1a8fb3f4b9b92d1ff65352b1a6e4ff9c) - [1148222](https://github.com/sendahug/send-hug-backend/commit/1148222cbdbd32607f18cbec1f9d32989bfda796)).

#### Fixes

- Fixed two potential vulnerabilities: Reflected server-side cross-site scripting in create_app.py and running Flask app in debug mode in production in app.py ([d1f7b81](https://github.com/sendahug/send-hug-backend/commit/d1f7b8157ff30d11fb2185d1fe43d855a5476112)).

### 2023-03-04

#### Chores

- Added a type parameter to all request args that aren't already typed ([a251b0e](https://github.com/sendahug/send-hug-backend/commit/a251b0ea21b8488112cd209b63862e556a071a6a)).

### 2023-02-26

#### Chores

- Migrated the tests from unittest to Pytest, which will allow us to split the tests according to the test subject, move the dummy data into fixtures which are reset automatically after every test, and parameterise tests to reduce duplicate code ([c0ca9ec](https://github.com/sendahug/send-hug-backend/commit/c0ca9ec3f07748937a80731d0438cefe385f72db) - [dd29135](https://github.com/sendahug/send-hug-backend/commit/dd29135d6ef8d760d49aaf5f3a42d249081122be)).

#### Documentation

- Adjusted the testing instructions in the README ([27f0297](https://github.com/sendahug/send-hug-backend/commit/27f029712c56cd94a9d6ac497a0400d0ceaabc7c)).

### 2023-02-25

#### Changes

- Split filter fetching from wordfilter check. While the word filter needs the "bad" words to filter out, it shouldn't be fetching them. Instead, they should be fetched in the context of the app and then passed into the filter. ([4e8636c](https://github.com/sendahug/send-hug-backend/commit/4e8636cb1f8987d8c62e3a16fff9e74d1637415a))
- Deleted unneeded checks for path params. Path parameters' existence checks are handled by Flask, so there's no need to validate that they exist manually. ([30717b9](https://github.com/sendahug/send-hug-backend/commit/30717b9afa48b4762f5d802a5990621ff8341429))

#### Chores

- Added further tests ([ffa2421](https://github.com/sendahug/send-hug-backend/commit/ffa242149e3a6034127d46c0b6c73d342fde4102)).

### 2023-02-12

#### Features

- Added a helper method for bulk inserts/updates ([8f522ee](https://github.com/sendahug/send-hug-backend/commit/8f522ee316b512b98b80f80b235e07fb93280763) & [fff806b](https://github.com/sendahug/send-hug-backend/commit/fff806b47394e1500b6c93c716c9cecd7b70311e)).
- Added on-delete/on-update rules to various foreign keys ([427e68e](https://github.com/sendahug/send-hug-backend/commit/427e68e3a598089272a5e48cab9a1d323f23e88a)).

#### Changes

- Moved the database-related error handling from the various endpoints to the relevant database helper functions. It doesn't really make sense to be doing the same error handling in multiple places when it's all related to the database. This also allows handling DBAPI errors related to bad data with the correct error code. ([7614d66](https://github.com/sendahug/send-hug-backend/commit/7614d669a20381b2dcf27c6f7bd4d463a6e342bd))
- Updated the multiple-users update in GET /users to use the new bulk update helper function ([2273bbf](https://github.com/sendahug/send-hug-backend/commit/2273bbfb54eaf054d8a57af904fec15b826dd5bd)).

#### Chores

- Replaced the methods' documentation with python docstrings ([d56ea87](https://github.com/sendahug/send-hug-backend/commit/d56ea875a77d40b4693772c34da6966909b650fc)).
- Added tests for more helper functions and fixed some tests' data ([4218a98](https://github.com/sendahug/send-hug-backend/commit/4218a9870d5a6dd30f64200b16c6e38faabe6fac) - [760a00a](https://github.com/sendahug/send-hug-backend/commit/760a00a3c99c581ac27f0cdf898fdb85c45a6e78)).

### 2023-02-11

#### Changes

- Replaced all `print` calls with logging to a proper python logger ([46e58f3](https://github.com/sendahug/send-hug-backend/commit/46e58f35ddaae56b4eeaf28f408dfe37b3e8fbb6)).
- Standardised the db helpers' responses to avoid confusion in the endpoints ([82065f0](https://github.com/sendahug/send-hug-backend/commit/82065f0b38d5afad81327a642665d5a98aeae4a2)).

#### Chores

- Fixed the typing in various parts of the app ([3ba34e6](https://github.com/sendahug/send-hug-backend/commit/3ba34e6d812dd567c34d26f334ef8d1ec23af9a5) - [f51612d](https://github.com/sendahug/send-hug-backend/commit/f51612dc6a9e693d5878bed5c240cd8850e56f14)).

### 2023-02-06

#### Chores

- Deleted an unneeded install step in CI ([ebec08e](https://github.com/sendahug/send-hug-backend/commit/ebec08e1376f5b8181cf8f6928c5a79262800070)).

### 2023-02-05

#### Features

- Added a new helper method for validating post/message texts ([449281a](https://github.com/sendahug/send-hug-backend/commit/449281a137c2ad8f5cac3d32a8cb5aaa8ad9de52)).

#### Chores

- Cleaned up more old code. This includes improved typing, simplified nested statements, and the removal of duplicate code ([c46c702](https://github.com/sendahug/send-hug-backend/commit/c46c7028cc43bb61e832535e0d4b4315654c0ca6) - [4065d5b](https://github.com/sendahug/send-hug-backend/commit/4065d5b9e9405bee268a12c0064179ee7d573d79)).

### 2023-01-31

#### Chores

- Added more tests for the app utilities ([001722b](https://github.com/sendahug/send-hug-backend/commit/001722bad1c799ef145cfefce4495448cb4b2991)).

### 2023-01-29

#### Changes

- Replaced the pagination mechanism with the built-in Flask-SQLAlchemy pagination mechanism. The previous pagination mechanism required fetching all the records from the database before doing any sort of pagination. This is extremely inefficient in large numbers and it makes more sense to do it in the database. ([a3b2d93](https://github.com/sendahug/send-hug-backend/commit/a3b2d93e814fc8443f89825e056984a58a213e52))
- Separated app setup from app creation. The app creation file should be purely for running the complete Flask app. The setup should be handled separately. Storing both in the same file was wrong ([ad20200](https://github.com/sendahug/send-hug-backend/commit/ad20200a43715c0f154ba078338ac843e2c63877)).
- Unified duplicate code in the messages' endpoints and moved the object count from the python code to the database ([9b3d91f](https://github.com/sendahug/send-hug-backend/commit/9b3d91f2bdf9fbcc8cb6f962b34a1cfdbdea60d3)).

#### Chores

- Fixed the URL used in one of the tests ([cda6a46](https://github.com/sendahug/send-hug-backend/commit/cda6a462a3712371ca7b34413067e21089e138c5)).
- Updated the versions of Python and Postgres in CI ([22575b9](https://github.com/sendahug/send-hug-backend/commit/22575b9bb4e6f5e384447022d31b45fd271fc471)).
- Split the dev requirements from the production requirements ([d558961](https://github.com/sendahug/send-hug-backend/commit/d558961ca0c6d61f941b3944e3ed723b450b5039)).
- Cleaned up the testing process ([24cbc5e](https://github.com/sendahug/send-hug-backend/commit/24cbc5ea2f2c7ae6f39c2dc89dbbf8a58b3ff7b9) - [87a675d](https://github.com/sendahug/send-hug-backend/commit/87a675d75523055520707ef61f289bcd3356be1d)). This includes:
  - Updated the way the database is initialised in tests.
  - Moved the tests' data to their own file.
  - Renamed the test database.
  - Adjusted the way the database is reset in tests.
- Deleted old unneeded files. These include pyup config (which isn't used anymore), files for Heroku deployment (also not used anymore) and an example of the environment setup. ([1bc0f30](https://github.com/sendahug/send-hug-backend/commit/1bc0f30b78b2d6db44193f7c781af4c1a8109d0f))
- Added mypy to CI and improved the app's typing ([2958465](https://github.com/sendahug/send-hug-backend/commit/29584654f9017d3d757290e0a3098d5840d0d8e0) - [7261693](https://github.com/sendahug/send-hug-backend/commit/726169316a824840a46fd0864c590112fc9ce39f)).

### 2023-01-02

### Changes

- Replaced the old "joined query" in the home route with a cleaner query written directly in the endpoint, instead of in another function ([9266815](https://github.com/sendahug/send-hug-backend/commit/92668155078af744f5f5136e368450e968c5924c)).
- Moved all the "joined query" queries from the joined query helper to the relevant endpoints ([1ebf2f0](https://github.com/sendahug/send-hug-backend/commit/1ebf2f01593f212e251b3f1c3809f18b97867fdb)).
- Updated the `format` calls to include extra keyword arguments instead of manually applying them later. For example, instead of manually adding the selected icon and icon colours to messages manually to the formatted object, we now pass these into the format call to get a properly formatted dictionary with all the data ([0893fdc](https://github.com/sendahug/send-hug-backend/commit/0893fdc5ce3fbf6745c79f034384fe61daedb077) & [b8f2677](https://github.com/sendahug/send-hug-backend/commit/b8f2677cf1f5c56acc5ca5ad04f746f68df694b5)).
- Messages' pagination now runs after the formatting, instead of beforehand ([1d890c2](https://github.com/sendahug/send-hug-backend/commit/1d890c277069fd57f04869756b408f38db24196c)).
- Combined the multiple SQL queries used to fetch threads into one query ([aee2c93](https://github.com/sendahug/send-hug-backend/commit/aee2c939b95f6fb9d77765ce747f0bba54b4416e)).

### 2022-12-27

#### Chores

- Moved the tests to a new tests directory ([a284889](https://github.com/sendahug/send-hug-backend/commit/a2848891c408b19ac0e7fd2211b65d16604dd729)).

### 2022-12-21

#### Changes

- Moved the filter and validator utilities to a new `utils` directory ([0105450](https://github.com/sendahug/send-hug-backend/commit/0105450a5e05ab76741cb15c895c6a99739f2b97)).
- Moved the database helper functions from the models' module to a new database-related module ([10bf93b](https://github.com/sendahug/send-hug-backend/commit/10bf93bec16d4804d21b776d7bb20475cf30fe3f)).
- Adjusted the way Flask-SQLAlchemy is initialised to correctly pass in the required settings ([f5851af](https://github.com/sendahug/send-hug-backend/commit/f5851afca5e7d3b007174e4747defe7be6b624ce) & [d2af058](https://github.com/sendahug/send-hug-backend/commit/d2af058990de28973fa446981d3e06a1fe684b59)).

#### Chores

- Simplified old code in the Validator ([2aa458a](https://github.com/sendahug/send-hug-backend/commit/2aa458a61a3e9ea461d455d702916903a384965c)).
- Deleted the unneeded PyOpenSSL dependency ([bdeeced](https://github.com/sendahug/send-hug-backend/commit/bdeeced78b40d8bd22a7dc0fff10a7c1e00789c2)).
- Added missing copyright notice ([d06ffee](https://github.com/sendahug/send-hug-backend/commit/d06ffee8bea03c69013334dd5be18699e4f5d1b5)).

### 2022-12-19

#### Changes

- Moved the push notifications' helper functions to their own module ([29b5a4f](https://github.com/sendahug/send-hug-backend/commit/29b5a4fa0b28e5eb1be1496625451e4e957c8229)).

#### Chores

- Added pre-commit to handle reformatting and linting the files ([/5f5a0a1](https://github.com/sendahug/send-hug-backend/commit/5f5a0a149f4b6ca40a8ca489b3e5105b518efe9e) - [9fb2588](https://github.com/sendahug/send-hug-backend/commit/9fb2588da87ffe0448881d9ae562f5aec3e9d620)).

### 2022-11-27

#### Chores

- Updated the copyright notices throughout the repo to include the current year ([bbd5138](https://github.com/sendahug/send-hug-backend/commit/bbd5138c78773020506394a5bedd3509401bb8d9)).

### 2022-10-09

#### Changes

- Changed the migration files' naming pattern. The new pattern starts with the date and time, so the migrations are now ordered according to their creation time ([71d3e00](https://github.com/sendahug/send-hug-backend/commit/71d3e00b1b990b663b4533391d9a1d9add0f1e11)).

#### Documentation

- Updated the README's instructions for running the app ([ec32d5f](https://github.com/sendahug/send-hug-backend/commit/ec32d5fed2ef6d34b782901e870899c50cdc793b)).

### 2022-08-14

#### Documentation

- Deleted the pyup badges from the README as they've switched to priced tiers only and those badges weren't particularly useful anyway ([0383362](https://github.com/sendahug/send-hug-backend/commit/038336206c9e16b82712d7d303a814ad4338eb77)).

### 2022-07-24

#### Chores

- Updated the Python runtime version in deployment ([ed2a9d4](https://github.com/sendahug/send-hug-backend/commit/ed2a9d4d6f6549fe0bd83fbbb8225e7182e75456)).

### 2022-06-19

#### Chores

- - Added a funding.yml file to enable sponsoring the team ([ae3d4db](https://github.com/sendahug/send-hug-backend/commit/ae3d4db96c57643f7db4e443bad5bca2ce128498)).

### 2022-06-18

#### Fixes

- Fixed a bug where endpoints handling user data returned an error due to an attempt to use `json.load` on a null value ([959e21a](https://github.com/sendahug/send-hug-backend/commit/959e21ab3854707bf3cc5ea6df26e1a7c692b5c8)).

### 2022-06-12

#### Changes

- Deleted the `manage.py` file, which was previously used to run migrations in deployment ([7ac21d1](https://github.com/sendahug/send-hug-backend/commit/7ac21d1f3fe968c903ecabe9e26798953d9c8844)).

#### Chores

- Deleted the flask-script dependency, which was removed in flask-migrate v3 ([6e734a9](https://github.com/sendahug/send-hug-backend/commit/6e734a9ebea781e0ebad3cdc473e73d341439d96)).

#### Documentation

- Updated the README with instructions for running database migrations in the production environment ([4f1237b](https://github.com/sendahug/send-hug-backend/commit/4f1237b3088382e71088d6f4e7630d9e63d1c63b)).

### 2021-07-02

#### Chores

- Changed the repository's primary branches to remove the reference "master" and to add a staging environment.
- Updated the GitHub Actions workflows to reflect the branches' change ([dd96397](https://github.com/sendahug/send-hug-backend/commit/dd963972e3332a42997b3807ef71260a745dbc34)).

### 2021-06-19

#### Chores

- Adjusted the `triggerbuild` action to allow Dependabot pull requests to trigger it. Since Dependabot is now unable to access repo secrets, an adjustment to the action was required to enable automated tests to run when Dependabot opens an update PR ([76cd929](https://github.com/sendahug/send-hug-backend/commit/76cd9290d8f67e5886fe1857c3f2cdb83796e3e4)).

### 2021-05-11

#### Chores

- Re-enabled dependabot's rebasing to easily resolve conflicts in its pull requests ([70b8b53](https://github.com/sendahug/send-hug-backend/commit/70b8b5303ef3e6437bdc27d25d8d2be068ee1710)).

### 2021-04-28

#### Chores

- Upgraded to GitHub-native Dependabot ([41c87c6](https://github.com/sendahug/send-hug-backend/commit/41c87c6945835eb8c2d1e85670b749b38545fe9a)).

### 2021-04-25

#### Chores

- Added a file specifying the Python version to use at runtime for deployment ([8670017](https://github.com/sendahug/send-hug-backend/commit/8670017d888a6d2f434757378db8c38079abe25a)).

### 2021-01-18

#### Chores

- Added a GitHub Actions workflow to automatically update the superproject repository when a release to live is made ([6c7e529](https://github.com/sendahug/send-hug-backend/commit/6c7e529b800604fdfeb7ee0b2ac9d0bf18b1a48d)).

### 2020-12-25

#### Chores

- Deleted the unneeded create-release GitHub Actions workflow ([e4ca4da](https://github.com/sendahug/send-hug-backend/commit/e4ca4da49f2fd8fe6ede3b8dc454c40bdd527a2e)).

## v1.0.0 Beta 2

### 2020-12-22

#### Features

- Added the users' icon data to the messages' endpoints to allow displaying the icons in the messaging views ([d831d53](https://github.com/sendahug/send-hug-backend/commit/d831d5327ab481d12bcb2def276e141e7a34d4f3)).

#### Fixes

- Renamed the keys in the icon colours' dictionary to match the expected keys in the front-end ([5826418](https://github.com/sendahug/send-hug-backend/commit/5826418335d32939f198d80daeee9492c87030df)).

#### Chores

- Updated the tests and the tests' data to include the new icon data ([717c383](https://github.com/sendahug/send-hug-backend/commit/717c38314bea793da4ad2e5fab66c15249c94c1a) & [b08fc76](https://github.com/sendahug/send-hug-backend/commit/b08fc76f662d6f5baef9db4ba3bec30ea90a3ca5))

### 2020-12-21

#### Fixes

- Fixed a string formatting error in the users' update endpoint ([eb351fd](https://github.com/sendahug/send-hug-backend/commit/eb351fdffe40798f85c48fc6333df87397e40798)).
- The default colours for the users' icons were set to the wrong values. They've now been updated to the correct values ([2088b42](https://github.com/sendahug/send-hug-backend/commit/2088b4295840d7c89cd46ecf5d39cb79e594f25d)).

### 2020-12-20

#### Features

- Added selected icon and icon colours columns to the users table to allow users to select an icon and its colours ([861fe99](https://github.com/sendahug/send-hug-backend/commit/861fe9945caacf69482e639870e3bbf990d2afce) & [041a0ac](https://github.com/sendahug/send-hug-backend/commit/041a0ac7886b0f51ad744a6d2dfd7fa5b1e70a9b)).
- Added the ability to update a user's icon and selected colours in the users' update endpoint ([a81e09a](https://github.com/sendahug/send-hug-backend/commit/a81e09a7fd09081dad64c42b7ec366d1f716e1d8)).

#### Chores

- Updated the test databases ([8c38c0e](https://github.com/sendahug/send-hug-backend/commit/8c38c0ecd2b28c546708e795e7dff82d55fe218e)).

### 2020-12-16

#### Chores

- Adjusted the GitHub Actions workflow and the CircleCI workflow to allow running tests only on pull requests made against the development and the live branches - based on an API request to the CircleCI API - or on commits pushed to either of those branches - based on the CircleCI config ([5426ed6](https://github.com/sendahug/send-hug-backend/commit/5426ed6d88f210b79b18f8d9c3e4fe793fc4db0f) - [24d60e7](https://github.com/sendahug/send-hug-backend/commit/24d60e78a1fbc36632dce179e984a93172aaaf63)).

### 2020-12-15

#### Chores

- Added an initial GitHub Actions workflow to trigger CircleCI builds ([a6aadda](https://github.com/sendahug/send-hug-backend/commit/a6aadda23bbbbe67156f8b0db5eda55d8ac85387)).

### 2020-12-08

#### Chores

- Set the CircleCI workflow to only run on specific branches ([b9ecca0](https://github.com/sendahug/send-hug-backend/commit/b9ecca0bad28cbb3b6b31c048b2d300251aff391)).

#### Documentation

- Replaced the # CI bradge in the readme with a CircleCI badge ([47354a2](https://github.com/sendahug/send-hug-backend/commit/47354a2a11321789b37bc3d31d969c64702ea307)).

### 2020-12-07

#### Chores

- Replaced the # CI config with a new CircleCI workflow ([fd8032d](https://github.com/sendahug/send-hug-backend/commit/fd8032d8b6bccf4ec0e64d37b7494421569b3341) - [a370cf6](https://github.com/sendahug/send-hug-backend/commit/a370cf68b9e6fd39dfe87ed05164e51c795722be)).

### 2020-12-06

#### Chores

- Added an initial CircleCI workflow file to run tests in CI ([f7d05fd](https://github.com/sendahug/send-hug-backend/commit/f7d05fdff661cbe751ec3f224eee22114b2a2b8c) - [72a2906](https://github.com/sendahug/send-hug-backend/commit/72a2906b4023166aacf0668b0bd6793a4e980399)).

### 2020-11-29

#### Chores

- Changed the create-release workflow to remove the branch restriction as a temporary workaround for it ([e1589fe](https://github.com/sendahug/send-hug-backend/commit/e1589fece668b1eabc9f799e54bc81a37078e366)).

### 2020-11-11

#### Chores

- Added a pyup config file ([4caa558](https://github.com/sendahug/send-hug-backend/commit/4caa55820b695b93aa1ec7b807f45b9d6402d390)).

### 2020-11-08

#### Changes

- Suggested posts are now sorted by date as well as hugs ([7b1c5fe](https://github.com/sendahug/send-hug-backend/commit/7b1c5fe9e4e2740e17ef76edca3c0cddad5da490)).

## v1.0.0 Beta 1

### 2020-11-06

#### Chores

- Added missing input to the GitHub Actions workflow for creating a release ([60feb4c](https://github.com/sendahug/send-hug-backend/commit/60feb4c1d9678b080092bbd773465e9accb03a04)).

### 2020-11-05

#### Fixes

- Added a missing query to count each thread's messages when fetching threads ([0f0e82c](https://github.com/sendahug/send-hug-backend/commit/0f0e82cf9cb5a6843a30df4b640aeaf774a78dfc)).

#### Chores

- Updated the tests and the tests' database ([38e8cc1](https://github.com/sendahug/send-hug-backend/commit/38e8cc1deec6b1583e9cef871512968e2a739787) & [df9cc96](https://github.com/sendahug/send-hug-backend/commit/df9cc96d14e59e507e722ff5f0b4f69b8b7734a8)).
- Added a GitHub Actions workflow to create a release ([3be45a16](https://github.com/sendahug/send-hug-backend/commit/3be45a160e413f3fdfd105266f65fe964bfb57ef)).

### 2020-11-03

#### Changes

- Reversed the order in which messages are shown to display the newest messages first ([3f6ed44](https://github.com/sendahug/send-hug-backend/commit/3f6ed448887b7cefe07c2216d8badddf7440367a)).

#### Fixes

- Previously, if a user deleted a thread and then sent/was sent another message to/from the user they had a deleted thread with, the thread wouldn't show as it was still considered "deleted". Now, if there's a new message, the thread's restored for both users, so that they can access it as they access all other threads ([34ed5e3](https://github.com/sendahug/send-hug-backend/commit/34ed5e31a7d758d6a31ac42c10293d27d70beb42)).

#### Chores

- Fixed an error in the DELETE filters test ([2b8eee2](https://github.com/sendahug/send-hug-backend/commit/2b8eee26b0aba088ec3de696603080cd0acabf1c)).

#### Documentation

- Added another badge to the main README ([0973b8d](https://github.com/sendahug/send-hug-backend/commit/0973b8ddae16ea383f3cf7bf564ec2f2ded4d2c2)).

### 2020-11-03

#### Changes

- Updated the Filter class's name to `WordFilter` to clarify its functionality ([4704901](https://github.com/sendahug/send-hug-backend/commit/4704901e4b4aa56667c4006265458bedbdf1c546)).

#### Fixes

- Fixed an issue in POST /filters endpoint where due to different casing, the same filters could be added multiple times ([33f1551](https://github.com/sendahug/send-hug-backend/commit/33f155123688bc26d5be676d6cb6345a0ebda559)).
- Fixed the values of the variables returned from the "create filter" and "update filter" endpoints. The expected structure in those endpoints changed once the filters were moved to a table, but they weren't updated, which caused an error ([5a865e2](https://github.com/sendahug/send-hug-backend/commit/5a865e27bbf793dcf1c01c09eb75f4779a94fc5b)).

#### Chores

- Updated the test database and the tests for the new filters table ([bf0cc5a](https://github.com/sendahug/send-hug-backend/commit/bf0cc5ab43d8eca466ac631cbf416060704b368c) - [f2dd1c1](https://github.com/sendahug/send-hug-backend/commit/f2dd1c19785c320b03b42cc6305a73f0c31d6465)).
- Fixed an error in the "delete filter" test ([2b8eee2](https://github.com/sendahug/send-hug-backend/commit/2b8eee26b0aba088ec3de696603080cd0acabf1c)).

#### Documentation

- Added another pyup badge to the README ([0973b8d](https://github.com/sendahug/send-hug-backend/commit/0973b8ddae16ea383f3cf7bf564ec2f2ded4d2c2)).

### 2020-11-02

#### Features

- Added a new filters table to contain the list of forbidden words ([42961c9](https://github.com/sendahug/send-hug-backend/commit/42961c9dee60f2cbc109a48ca722c3d2f5191b96) & [f86d217](https://github.com/sendahug/send-hug-backend/commit/f86d21757ec8703b872ef4c8f635ba58d6dc43e2)).

#### Changes

- Replaced the Wordfilter with a new strcture based around the new filters table. Instead of relying on the Wordfilter package to supply an initial list of words and updating that list in the app, we now keep all the words that should be filtered in the database and run CRUD operations against it the way we do with all other objects ([60cc8fe](https://github.com/sendahug/send-hug-backend/commit/60cc8fea8718750615e0eabd0c29f8364c05997e) - [b434431](https://github.com/sendahug/send-hug-backend/commit/b434431c8017572e631ffbc2ff02977d68e5351b)).

### 2020-10-30

#### Chores

- Added templates for pull requests ([eb173d7](https://github.com/sendahug/send-hug-backend/commit/eb173d78176a25c029fa35a3e34e432c48671747) - [aee8cd8](https://github.com/sendahug/send-hug-backend/commit/aee8cd887e3911c298e3fc6ab20ddc39f8abfda2)).

### 2020-10-29

#### Chores

- Added code of conduct to the repo ([af5ed0d](https://github.com/sendahug/send-hug-backend/commit/af5ed0dca9ebe501edf74b5d320cb2933ee4792a)).
- Updated the GitHub issue templates ([880330f](https://github.com/sendahug/send-hug-backend/commit/880330fee9330629487ea988816f3f9c5a72b1a4)).
- Added a CONTRIBUTING file to provide information about contributing to the repo ([44f240f](https://github.com/sendahug/send-hug-backend/commit/44f240f9a0c01bda003d5281603b04e3d77f07f4)).

#### Documentation

- Added the new push subscriptions endpoint to the API documentation ([93afbc7](https://github.com/sendahug/send-hug-backend/commit/93afbc75d37b00ea66d8327fad4a8cfe97b6ff3b)).

### 2020-10-28

#### Features

- Added the ID of the added push subscription to the response from the "add push subscription" endpoint ([e9f7d51](https://github.com/sendahug/send-hug-backend/commit/e9f7d51bd8458ce450b7605b4e392b906944567e)).
- Added an endpoint to update existing push subscriptions ([99d73a3](https://github.com/sendahug/send-hug-backend/commit/99d73a32f72dd4682fa726a8e348663f68235c1f)).

#### Chores

- Added templates for opening new issues in GitHub ([eaafdd7](https://github.com/sendahug/send-hug-backend/commit/eaafdd7f815bda7ac22545db875aa64da44a5a6c)).

### 2020-10-02

#### Chores

- Updated the license to add a clause about copying the project ([5c3e18d](https://github.com/sendahug/send-hug-backend/commit/5c3e18deda6fa5eaffa385c053dd4d242d8a6ce0)).

#### Documentation

- Removed the license badge from the README ([62bf34f](https://github.com/sendahug/send-hug-backend/commit/62bf34f2de232f414c867daa31155235a0233fc8)).

### 2020-10-01

#### Chores

- Added Dev branch back to testing. Since there aren't many commits made to "Dev" or "live", there was no need to limit the branches being tested ([4b01dc7](https://github.com/sendahug/send-hug-backend/commit/4b01dc704515a16970c921d692fd0b3d85446780)).

### 2020-09-19

#### Features

- Added the forbidden words to the error message returned by the API on validation errors to allow the users to fix their text ([b6ebe7b](https://github.com/sendahug/send-hug-backend/commit/b6ebe7b00e2b626bef549e3c1903bf35210e16c8)).

#### Documentation

- Updated the README's badges ([e3004db](https://github.com/sendahug/send-hug-backend/commit/e3004dba2821ae4597b7daa26c2380e4aee75a66)).

### 2020-09-14

#### Chores

- Updated dependencies ([f8a8386](https://github.com/sendahug/send-hug-backend/commit/f8a8386b6794edc190882052454a59e76f774a63)).

### 2020-09-10

#### Chores

- Updated the tests' database (and the command used to restore it) to exclude postgres's roles ([968a873](https://github.com/sendahug/send-hug-backend/commit/968a8730e0e942f4392670eaf0bd9214cb71732d) & [5cdc941](https://github.com/sendahug/send-hug-backend/commit/5cdc9413b1633b90e3079246ad6860c08f3c9769)).
- Added database dump to import before running the tests. This is required right now due to a Postgres bug that causes errors when trying to restore a database via `pg_restore` (whereas it works fine via `psql`). Once the database was restored via `psql` (or even via `pg_restore`), `pg_restore` works fine; the first restoration seems to be the problem. Since `psql` doesn't seem to work on Python (through the sh package), right now both archives are required: the sql dump is needed to run `psql` restoration, and the custom dump is needed to run `pg_restore` during tests. ([10f2941](https://github.com/sendahug/send-hug-backend/commit/10f294109b1e88a5a23fc136174580436452bdd9))
- Removed the main branch from CI's triggers to ensure we're not calling the Auth0 client too much ([2b2660f](https://github.com/sendahug/send-hug-backend/commit/2b2660f3bd63461bac4c27650cc7c6f695b9e57c)).

#### Documentation

- Added coverage badge to the main README ([4cf6d08](https://github.com/sendahug/send-hug-backend/commit/4cf6d081035173e684a1bd7c93cf6d1f4d0b08c4)).
- Updated the testing and usage instructions in the README ([3b550b7](https://github.com/sendahug/send-hug-backend/commit/3b550b77143ad5447df18fb2321df55eb5241063) & [9a16f85](https://github.com/sendahug/send-hug-backend/commit/9a16f85fbccf4eb144ab615fd517d9ca756b8ec6)).

### 2020-09-09

#### Fixes

- Added missing "thread" message type to the "delete message" endpoint to allow deleting messages from the single thread view ([84a5208](https://github.com/sendahug/send-hug-backend/commit/84a52083b11c5cac37565d2c463f0f727fdd85a5)).
- Fixed the list index in the filters' delete endpoint ([cf80bcf](https://github.com/sendahug/send-hug-backend/commit/cf80bcf0ec492b779b6f070f8d0e43be644e9b0d)).
- Changed the way the app checks whether a filter exists in a given index, which fixes an "out of bounds" error ([cf80bcf](https://github.com/sendahug/send-hug-backend/commit/cf80bcf0ec492b779b6f070f8d0e43be644e9b0d)).
- Added a check for whether a thread exists before attempting to use the SQLAlchemy object, which caused a "NoneType has no attribute" error in the "read user messages" endpoint ([549832a](https://github.com/sendahug/send-hug-backend/commit/549832af17963a867b81221a47b22e2062f93dc8)).

#### Chores

- Updated `psycopg2-binary` to v2.8.6 ([15a7bfb](https://github.com/sendahug/send-hug-backend/commit/15a7bfb06d7188b3a4519bb22e8d5fef6ce96629)).
- Fixed further errors in tests ([4b28c32](https://github.com/sendahug/send-hug-backend/commit/4b28c329f8dfe2fe808a0d9f5f4f6672ca582c61) & [cefb898](https://github.com/sendahug/send-hug-backend/commit/cefb8985b8aa94be9d6b8648ebec61ca65d62d57)).
- Added an initial # CI workflow to run unit tests in CI ([60d3b9b](https://github.com/sendahug/send-hug-backend/commit/60d3b9b80cebee84c9c911a45a1fe8aa9d7cde05) - [2bd3e69](https://github.com/sendahug/send-hug-backend/commit/2bd3e69a2a5501a4d68a45a6ce143102ade08ec5)).
- Updated the tests database ([4748da3](https://github.com/sendahug/send-hug-backend/commit/4748da3894913f641e5083f2502bfdd1b483edec) & [333170e](https://github.com/sendahug/send-hug-backend/commit/333170ee1bcbe8cb21326bbeed8d044c1db7734b)).

#### Documentation

- Updated the testing instructions in the README ([5218631](https://github.com/sendahug/send-hug-backend/commit/521863184ae90554a927a26653a39a75d49009e6)).

### 2020-09-08

#### Features

- Added a helper method for updating multiple SQLAlchemy objects at once ([22b119e](https://github.com/sendahug/send-hug-backend/commit/22b119e8779522909e4b95a4157cadf7cb9fa6d5)).
- Added a permission check to the posts' update endpoint to ensure non-admins can't close a report via that endpoint ([fcd74ce](https://github.com/sendahug/send-hug-backend/commit/fcd74ce213bc5f778ae6fb47a7e541d822084417)).
- Added a check to the users' edit endpoint to ensure users can't update other users' settings ([20ea747](https://github.com/sendahug/send-hug-backend/commit/20ea747894b525f5040927ed8fcf535cffd6a54a)).

#### Changes

- The posts' update endpoint now updates objects using the bulk update method instead of the single update method ([be4f805](https://github.com/sendahug/send-hug-backend/commit/be4f8051616dc274e2bec83aff12e3deda354106)).

#### Fixes

- Fixed a bug comparing user IDs in posts and messages DELETE endpoints. The user ID was treated as a string in the permissions check, which caused the condition to return `False` even when the user was trying to delete their own posts ([e491483](https://github.com/sendahug/send-hug-backend/commit/e4914833ff32140b6ad3e156316a1be777733c99) & [c52a34c](https://github.com/sendahug/send-hug-backend/commit/c52a34c630dcbc68454d67ccbf3776b69e88047c)).
- Fixed an error in the new report, new message and new post endpoints, in which the wrong value was assigned to the 'new item' variable and returned to the user ([c81ed84](https://github.com/sendahug/send-hug-backend/commit/c81ed84bfcec7c6be4acef2b7281afa70a5ea631) & [7b12c30](https://github.com/sendahug/send-hug-backend/commit/7b12c30de87602c92cff989c16ed854bbeaec63e)).
- Added missing checks to the "create report" endpoint to ensure the post/user being reported actually existed before trying to create a report ([a12a4d6](https://github.com/sendahug/send-hug-backend/commit/a12a4d6d0c3339716211c56ba0463e35833259ce)).

#### Chores

- Changed the way the database is set up and reset between tests. Now, The database clearing runs after every test, and the initial creation is removed (as it's re-created before the first test anyway). ([0170f55](https://github.com/sendahug/send-hug-backend/commit/0170f55e8838296176e8c26065c4f5bd2c763bd2) & [6e289f2](https://github.com/sendahug/send-hug-backend/commit/6e289f22fa8a9f017aeb5db131c5eb525ac346cb))
- Fixed an error in tests that caused the test users' token not to be updated in the authorisation headers ([145491a](https://github.com/sendahug/send-hug-backend/commit/145491a863864e093e9fb668c2fbac2e4f5014d5)).
- Updated the tests' database and the process through which the database is getting restored ([55580bc](https://github.com/sendahug/send-hug-backend/commit/55580bcc8aef0b6d2b427cd99c861b5cdd4e8b19) - [643086e](https://github.com/sendahug/send-hug-backend/commit/643086e6df0b9392420e8db99ca92bce1c97b1d4)).
- Fixed errors in the home, search and posts endpoints' tests ([3e8bfbc](https://github.com/sendahug/send-hug-backend/commit/3e8bfbcc56f6bc3d5df25372534d2cf00322d92c)).
- Fixed errors in user, messages, reports and filters tests ([9e50bcd](https://github.com/sendahug/send-hug-backend/commit/9e50bcdcd8a148c5a9e31875ab366c3de2bb89f6) & [1adccf1](https://github.com/sendahug/send-hug-backend/commit/1adccf1d74f3f660d7145acefe8227438ed5c2f2) & [1e96c69](https://github.com/sendahug/send-hug-backend/commit/1e96c69e952e0785d3a3021059ab71faa4904a05)).

### 2020-09-05

#### Chores

- Replaced http.client library with urllib.request in tests ([cc43ddc](https://github.com/sendahug/send-hug-backend/commit/cc43ddc91bf13215a71bfcae6b50f035288dc0b0)).

### 2020-09-04

#### Fixes

- Fixed an error in new user workflow where the wrong value was assigned to the "new user" variable and returned by the API ([18650ca](https://github.com/sendahug/send-hug-backend/commit/18650cad5c2c62e50c7a715be1e522a55f3ef01c)).
- Fixed the URL encoding in the management API token fetch ([5092546](https://github.com/sendahug/send-hug-backend/commit/5092546ae81a3752c48e9a0ac4aed39220e6a561)).

#### Chores

- Added token getter for each of the test users in unit tests. This is meant to be a set up for automated unit-testing. Each user's token is fetched via Auth0's Resource Owner Password Grant and is then saved and used for performing the relevant user's tests. ([645b439](https://github.com/sendahug/send-hug-backend/commit/645b439901c216a6a20d28df404e9f984763298d) & [8fe91e1](https://github.com/sendahug/send-hug-backend/commit/8fe91e1f1b4094c8d415cff542ad92d9923cedf6))
- Adjusted the test data and database ([eb3f5ad](https://github.com/sendahug/send-hug-backend/commit/eb3f5ad6773665a233f92afd8ccb7781a83a406a) & [2b7d51f](https://github.com/sendahug/send-hug-backend/commit/2b7d51fba84b775a26b014bb242ac0ca3a2f8559)).

### 2020-09-03

#### Chores

- Updated dependencies ([0f13984](https://github.com/sendahug/send-hug-backend/commit/0f139847964fc6cec656c7be38bc82d00e2b79ba)).
- Deleted the workflow for automatically pushing updates to the mirror repository, which was added in [77a6610](https://github.com/sendahug/send-hug-backend/commit/77a6610728026267cf067d413b315bedc620efc7) ([a0947a3](https://github.com/sendahug/send-hug-backend/commit/a0947a31e460e10adda0740442c625c6a60e447b)).

#### Documentation

- Added the pyup status badge to the README ([8fc289d](https://github.com/sendahug/send-hug-backend/commit/8fc289dfa3e78344f3a0cc87d1f49aed1466618f)).

### 2020-08-31

#### Chores

- Updated dependencies ([d6feaf9](https://github.com/sendahug/send-hug-backend/commit/d6feaf91500b92007465443f851a77565a3879fe)).

#### Documentation

- Added build status badges to the README ([aa67494](https://github.com/sendahug/send-hug-backend/commit/aa67494d88b2a93d1f683dc9739ca903570f1dd9)).

### 2020-08-18

#### Fixes

- Fixed an error accessing the response of the request to refresh the management API token ([f3411a9](https://github.com/sendahug/send-hug-backend/commit/f3411a9d2efdb61668f89a580e336107c60d77fa)).

### 2020-08-17

#### Chores

- Added a license file ([95ec13b](https://github.com/sendahug/send-hug-backend/commit/95ec13ba3d82a8d2a34998bfc3e4b5b3f7181a76)).
- Added the license to all script files ([24a14ad](https://github.com/sendahug/send-hug-backend/commit/24a14ade06e28712cd981355bedbff42d76af730)).

### 2020-08-09

#### Documentation

- Renamed the API Documentation file ([057abf6](https://github.com/sendahug/send-hug-backend/commit/057abf696de627e1761205aac08d198d364085b1)).

### 2020-08-01

#### Changes

- Changed added objects' return data ([0e6eed4](https://github.com/sendahug/send-hug-backend/commit/0e6eed41855aa438ffdc48104bd59135837545d3)).

#### Fixes

- The Auth0 management API token now correctly establishes an HTTPS request instead of an HTTP request ([20dff64](https://github.com/sendahug/send-hug-backend/commit/20dff64596ad2f726ac53cf72b3c74ccec458e54) - [e76463a](https://github.com/sendahug/send-hug-backend/commit/e76463a010655522c0ff125b8e70f0996dd0ba56)).
- Added a condition to properly mark "user" roles upon user update, as we previously only had checks for "admin" and "moderator" roles ([5ee19f9](https://github.com/sendahug/send-hug-backend/commit/5ee19f97797477ff07800590d92523dad07e2be6)).
- Fixed syntax errors in the Validator, where the constraints were accidentally accessed with an object's dot notation instead of with the dictionary's format ([91482bc](https://github.com/sendahug/send-hug-backend/commit/91482bc2112b4db1a2cd2f48518fe56d19086e20)).
- Fixed a bug where messages sent between users who didn't have an established thread didn't trigger the creation of a new thread ([5ef2f10](https://github.com/sendahug/send-hug-backend/commit/5ef2f10b938cb18dfb0c083367ddfd5cabfabec9)).

### 2020-07-31

#### Changes

- The new user's "create user" process has been adjusted to automatically change the user's role upon creation. Previously, a new user would be assigned the "new user" role in Auth0, which gave them permission to create a user in the API. However, once they were created, their role needed to be changed manually (to the "user" role) in the Auth0 UI. This ensures the change is made automatically using the Auth0 API instead to prevent them from creating new users that do not exist in the Auth0 users database ([f4ddc46](https://github.com/sendahug/send-hug-backend/commit/f4ddc464042ba1051824b166222b1f10a4201b43) - [dfa6c03](https://github.com/sendahug/send-hug-backend/commit/dfa6c036312fa53c9fd28bc47c1ab2ca7d1336e6)). The change includes:
  - Added the process for changing the user's role using an API call to the Auth0 API.
  - Added methods for refreshing the Auth0 Management API tokens used for the role update.
  - Adjusted the user endpoints to the new structure.

#### Fixes

- Fixed a bug where first login caused an issue getting user data due to a number (the user's internal ID) being treated as a string ([700ec9a](https://github.com/sendahug/send-hug-backend/commit/700ec9a78b7bb65118210513ae749a52593ac633)).

### 2020-07-24

#### Features

- Added a "refresh rate" column to the users' table to indicate how often users want their notifications to be refreshed in the background ([1fff031](https://github.com/sendahug/send-hug-backend/commit/1fff031a2f16b9b958079d2e10c45a276abd0ae2)).

#### Fixes

- Added missing setup for settings-related attributes in the users' creation and edit processes ([7670744](https://github.com/sendahug/send-hug-backend/commit/767074440a9ac8f413b6f9042b60466ebd69916e)).

### 2020-07-22

#### Fixes

- Fixed a bug with sent_hugs list where we accidentally added empty items to the list ([2c8bc20](https://github.com/sendahug/send-hug-backend/commit/2c8bc207b6aa6a0b24204a21471bd541b8dca6ee)).

### 2020-07-21

#### Features

- Added the list of the users who sent hugs for a post to the post JSON returned by the API ([85cb8b1](https://github.com/sendahug/send-hug-backend/commit/85cb8b110fe028046f340923c18fe6d58124d8ff)).

#### Fixes

- Added a missing comma in the conversion process between strings (the way the `sent_hugs` list is stored in the database) and lists (the way the back-end and front-end treat the list). ([b0362c3](https://github.com/sendahug/send-hug-backend/commit/b0362c33acbaa41153185a41f2485499d30a28a3))

### 2020-07-20

#### Features

- Added a column to the posts' table which keeps track of the list of users who sent a hug for it ([2629f3d](https://github.com/sendahug/send-hug-backend/commit/2629f3dbacd8b2b363099a7a4ad5082c0897a03c) & [ffeb4e8](https://github.com/sendahug/send-hug-backend/commit/ffeb4e87a1ebeaf1eeefee64279d5260634b182c) & [e36d57a](https://github.com/sendahug/send-hug-backend/commit/e36d57add969dd93cd1c6a580dd50a903a7593e4)).
- Added a check in posts' edit to ensure that the same user doesn't send hugs for the same post more than once ([d06ccac](https://github.com/sendahug/send-hug-backend/commit/d06ccacbb83cc2158747df573413569a8045978d)).

### 2020-07-19

#### Features

- Added type validation for all user inputs ([3095d51](https://github.com/sendahug/send-hug-backend/commit/3095d51c586c57fc01719f2a2196df38cbd8aeb1)).

#### Changes

- Moved all the validation checks (type, length and text) to a new Validator class ([84b25b4](https://github.com/sendahug/send-hug-backend/commit/84b25b4f09451c15e563a4d33f215bf3d2e80e61) - [e5fc353](https://github.com/sendahug/send-hug-backend/commit/e5fc3534b7c499e03c4c33d8020f255f1a2c1da0)).
- Deleted an unneeded check that ensured the report reason was a string. Since the front-end always returns a string, that check was unnecessary ([a8da26d](https://github.com/sendahug/send-hug-backend/commit/a8da26da059b481c8b788c597d94199fe27e35b2)).

### 2020-07-18

#### Features

- Added a helper method for checking whether a text contains blacklisted words ([cdd6e04](https://github.com/sendahug/send-hug-backend/commit/cdd6e04b0a937caa70387c9748676396ee30be8c)).
- Added a special validation error (and a handler for it) to use when the user input isn't valid ([13cec90](https://github.com/sendahug/send-hug-backend/commit/13cec90b3df6ee3a0fc3b554dafecc77bc6af830) & [4105a8f](https://github.com/sendahug/send-hug-backend/commit/4105a8f128bd765f2f6bebea4837475049bc14df)).
- Added word filtering to posts and messages. If the user's text for any of those contains a blacklisted word (or more), a validation error is thrown instead ([863f5a6](https://github.com/sendahug/send-hug-backend/commit/863f5a620f5e1981b13c5ae913cc5adc73f0ab76) - [6f9e355](https://github.com/sendahug/send-hug-backend/commit/6f9e355f9ebb3762a261f22e291852e8a7b2dc97)).
- User posts are now ordered by date ([4204bad](https://github.com/sendahug/send-hug-backend/commit/4204bad10c07caf9df12df30d26981f49a6de2fd)).
- Added length checks for all user inputs ([38a3bc9](https://github.com/sendahug/send-hug-backend/commit/38a3bc908f3efcf8340205616945a66fcdd3c657) & [42eee66](https://github.com/sendahug/send-hug-backend/commit/42eee666df5b3c86b5071ea152619621758813ee)).

#### Fixes

- Previously, when users tried to update their own display name, the update was ignored due to a missing if/else branch (we only had handling for cases where the user tried to update someone else's display name). The missing branch was added to the if/else clause ([036f006](https://github.com/sendahug/send-hug-backend/commit/036f0065454843c372788c29035984174eb8e401)).

### 2020-07-17

#### Chores

- Added a new workflow for automatically pushing updates to the main repo to the private mirror of it ([77a6610](https://github.com/sendahug/send-hug-backend/commit/77a6610728026267cf067d413b315bedc620efc7) & [fd76ecf](https://github.com/sendahug/send-hug-backend/commit/fd76ecf2bc7579b4d34261ef50cf73605ba49f74)).

### 2020-07-16

#### Chores

- Updated the test process to include a database reset between tests. This ensures that all tests are fully independent and can run in any order ([818aed5](https://github.com/sendahug/send-hug-backend/commit/818aed58663347121b87fd8e97a12b6708f76a88) & [36bf4eb](https://github.com/sendahug/send-hug-backend/commit/36bf4ebfd016bf5114e0a960d830f95fc5493340)).
- Added more unit tests and updated existing tests' data to match the reset database ([9e6dd31](https://github.com/sendahug/send-hug-backend/commit/9e6dd31486cac15491250d09c660d071be4c5011) - [9c54965](https://github.com/sendahug/send-hug-backend/commit/9c54965934bbf2fed2b6f37e2be09c5116e40c5c)).
- Moved the JWTs used by the tests to environment variables, which makes them easier to replace and to keep out of the repository ([9c54965](https://github.com/sendahug/send-hug-backend/commit/9c54965934bbf2fed2b6f37e2be09c5116e40c5c)).
- Updated the tests' database ([33037be](https://github.com/sendahug/send-hug-backend/commit/33037be5ca2527087e6f833ee01aa9d1101ac0af)).

#### Documentation

- Updated the README with details about the database-reset and the JWTs in tests ([8dc9e78](https://github.com/sendahug/send-hug-backend/commit/8dc9e783f756fcc9b1aaa7fd1a232f0cf1bb9f16) & [f141352](https://github.com/sendahug/send-hug-backend/commit/f1413521e020286a9b624ff795f1a108b4d6fcda)).

### 2020-07-15

#### Features

- The user-related endpoints now also return the date in which the user last read their notifications ([6e56f80](https://github.com/sendahug/send-hug-backend/commit/6e56f804f60e2e4ec64b6ed661c59edeeee6dad0)).

#### Chores

- Updated the tests' database ([0e89123](https://github.com/sendahug/send-hug-backend/commit/0e89123478deda0b0e33a4aeb26bd438ad3a233d)).
- Added further tests for new endpoints and scenarios ([3d2f081](https://github.com/sendahug/send-hug-backend/commit/3d2f0815fea3a90c4fde6fa3774af05f4e240716) - [bbf63b0](https://github.com/sendahug/send-hug-backend/commit/bbf63b0d41bf946b80582bdbff4a086ab04bd2bf)).

### 2020-07-14

#### Chores

- Updated tests and added tests for the new endpoints ([9b83d25](https://github.com/sendahug/send-hug-backend/commit/9b83d258d4b3dde58809c71fc0e9f57f947a7f18) - [26429e8](https://github.com/sendahug/send-hug-backend/commit/26429e8f36992307e23d2dddf87bfe1b896897b1)).

### 2020-07-09

#### Features

- The "read all users by type" endpoint now also automatically unblocks users whose release time has passed ([9ae0812](https://github.com/sendahug/send-hug-backend/commit/9ae081298fe22f5ff3c45263f4a3193a9f0d89f0)).
- Added new columns to the users table to indicate whether the user enabled push notifications and auto-refresh for notifications ([8046f76](https://github.com/sendahug/send-hug-backend/commit/8046f768854541a61ac2ef001360f25cd939d755) - [ce96b5c](https://github.com/sendahug/send-hug-backend/commit/ce96b5c72b9f197e29393a0f801692fd449c23a5)).

#### Changes

- Changed the structure of the push notifications to include a title with the type of notification (for hug/message) and a text indicating who sent the hug/message ([54109d3](https://github.com/sendahug/send-hug-backend/commit/54109d32a2a11e1dfbb8661dba585e0d4743fa63)).

#### Fixes

- Fixed an incorrect column name in the "edit user" endpoint ([307ce14](https://github.com/sendahug/send-hug-backend/commit/307ce145b7feefb6cabae58770864f4e36a9b92a)).
- Non-silent notification refreshes were previously not possible because the notifications endpoint expected a boolean for `silentRefresh`, but the front-end sent it in the JavaScript format (`false`), which isn't a valid boolean in Python. As such, it was discarded. The parameter is now set to be a string, and the endpoint includes a check for `false` as the value ([9168569](https://github.com/sendahug/send-hug-backend/commit/916856918520f44c3b6dda102195f2382061b8bc)).

### 2020-07-08

#### Features

- When a user sends a message or a hug, the API now adds a notification to the user's notifications with details about the hug/message ([4fc9707](https://github.com/sendahug/send-hug-backend/commit/4fc9707e9458f6d856e8ecc1249b0e95c15f9552)).
- Added support for push notifications for hugs/messages ([fc460ec](https://github.com/sendahug/send-hug-backend/commit/fc460eccb77bc62a813f151de179e53f222b539e) - [955a81b](https://github.com/sendahug/send-hug-backend/commit/955a81bd9d27a25e0fd6d96fd2a623d3508067bb)). This includes:
  - Added a subscriptions table to store push subscriptions.
  - Added an endpoint for adding a new push subscription.
  - Added a helper method for creating and sending push notifications,
  - Set the "edit user", "edit post" and "send message" endpoints to send push notifications when the user is sent a new message or a hug.
- Added the ability to refresh the "new notifications" list without updating the "last read" date in the users table (i.e., a silent refresh). ([e4803d3](https://github.com/sendahug/send-hug-backend/commit/e4803d35600e70043a0bc5e74a260d0c21b28b2d))

### 2020-07-07

#### Features


- Added support for user notifications for hugs/messages ([356b787](https://github.com/sendahug/send-hug-backend/commit/356b7875ed4e3e2191b387c1e5920fc47c64e0c9) - [7d0d425](https://github.com/sendahug/send-hug-backend/commit/7d0d425d1c1244f73b0d6f4f96d74755ae0c0801)). This includes:
  - Added a column to the users table which indicates when the user last read their notifications.
  - Added a notifications endpoint for fetching notifications.
  - Added a notifications table for storing user notifications.
- Installed pywebpush to enable sending push notifications.

### 2020-07-06

#### Fixes

- Fixed an error where a deleted reported item caused the "report closing" process to error because the endpoint was trying to update the delete item's report status ([294347e](https://github.com/sendahug/send-hug-backend/commit/294347e027ad72b9ead56e568a3d79e0411e7e57)).

### 2020-06-29

#### Fixes

- Fixed an error that caused the suggested posts' fetch to fail due to an undefined variable ([753d465](https://github.com/sendahug/send-hug-backend/commit/753d465b7206f8a762e194bfbac5b1512d6cf934)).

### 2020-06-28

#### Features

- The user messages returned by the API now include the ID of the containing thread ([2fc1227](https://github.com/sendahug/send-hug-backend/commit/2fc1227be22895d60fca69438600f590de2f0026)).

### 2020-06-24

#### Documentation

- Fixed the links and parameter names in the API documentation ([b60b0ab](https://github.com/sendahug/send-hug-backend/commit/b60b0ab6376408726568f8d911c5898c976ba8eb) & [3db7869](https://github.com/sendahug/send-hug-backend/commit/3db7869617c364f9d79b4433c83978cbf0b6a9d7)).

### 2020-06-23

#### Features

- Added the ability to delete messages and threads. This includes:
  - Added new columns to messages and threads to indicate whether each of he users deleted the message/thread ([a57d90f](https://github.com/sendahug/send-hug-backend/commit/a57d90fa9362a26d9a3bbe704ae06d05732c3e96) - [9fb551b](https://github.com/sendahug/send-hug-backend/commit/9fb551bae336f8fc7cbdd2f9c79475707a5639e7)).
  - The message/thread is deleted from the database entirely only if both users deleted it ([df9c655](https://github.com/sendahug/send-hug-backend/commit/df9c655db923dc7f019a10c73f4c105604575703) & [25d44f8](https://github.com/sendahug/send-hug-backend/commit/25d44f8ea1a87d37bf9f10964b9d2da0017b4164)).
  - Messages and threads deleted by the user no longer show when fetching messages and threads ([9a9754c](https://github.com/sendahug/send-hug-backend/commit/9a9754cdf5fb9f021c0474b6c9be552295d63a49) & [b889082](https://github.com/sendahug/send-hug-backend/commit/b8890828d0bf87934425749af7dbea8c9a270a9c)).
- When the user deletes a thread, this now automatically deletes all messages in it ([26003bc](https://github.com/sendahug/send-hug-backend/commit/26003bc5922adb9eca368bc754768b21fa9c64d7)).
- If the user was blocked and their release date passed, the API now unblocks the user automatically ([5cb07c0](https://github.com/sendahug/send-hug-backend/commit/5cb07c015acc9c254f5223c2c19a6dd964fb1ed8)).

#### Documentation

- Updated the README and the API documentation with details about the new endpoints and modules ([c567a72](https://github.com/sendahug/send-hug-backend/commit/c567a72ce007ff960a263ad47b2a91ae815a637a) & [8fc5647](https://github.com/sendahug/send-hug-backend/commit/8fc564799f1b329465d81905b9a4a64a2422e584)).
- Added a table of contents to the API documentation to allow jumping to specific endpoints ([78756d2](https://github.com/sendahug/send-hug-backend/commit/78756d2dbdfdeca5a48b7e000941bde468d0163c)).

### 2020-06-22

#### Features

- Added the block-related properties to the formatted user JSON sent back by the API ([9d4ec62](https://github.com/sendahug/send-hug-backend/commit/9d4ec62e28d4ab102672b450fd8f1e4740cb8916)).
- Added a check to prevent blocked users from posting new posts ([89c1021](https://github.com/sendahug/send-hug-backend/commit/89c10218e5c95dd0c7e3e780f8482a62acd5157e)).
- The post and user edit endpoints now close any open reports against the post/user if the admin chose to close the reports ([4bd0700](https://github.com/sendahug/send-hug-backend/commit/4bd07001b8dc472712e0b9577c187db452fa3a8f) & [e621548](https://github.com/sendahug/send-hug-backend/commit/e62154890107016fc9785c1b1322697343d3783f)).

#### Changes

- Changed all user endpoints to include the `all` prefix (as the user type) for consistency ([7de62bd](https://github.com/sendahug/send-hug-backend/commit/7de62bdbb4ac1ce9590a552dc368acd9a1ff880f)).

#### Fixes

- Fixed a bug where attempting to access the `/users/:user_id` endpoint errored with an "invalid argument" because the request was sent to the new `users/:user_type` endpoint instead. This was fixed by adding `all` as the user type to the "read user" endpoint ([4732622](https://github.com/sendahug/send-hug-backend/commit/473262293e23682db7a62fe9d351f9a7f0fd14c1)).
- Fixed a bug referencing a variable before assigning it in the "get users by type" endpoint ([2494775](https://github.com/sendahug/send-hug-backend/commit/2494775cc3824e171a1ca0add40f90c8ebbed298)).
- The "get open reports" endpoint was accidentally assigning the wrong value to the user and post reports variables. The endpoint was updated to get the right values from the joined query ([383b226](https://github.com/sendahug/send-hug-backend/commit/383b226ce173eba39a29d28be44c59c0508421ab)).
- Previously, if a post update didn't contain hugs data, the posts' update endpoint errored. This caused an issue for updating a reported post (which didn't have details about hugs included). The endpoint was updated to check whether there's data about hugs in the incoming request before attempting to update the post's hug ([950b7fd](https://github.com/sendahug/send-hug-backend/commit/950b7fdfbce9db6f641903595803498423a52a8a)).
- Fixed an error in report type filtering in the GET "reports" endpoint, which caused the endpoint to return zero results even when there were open reports ([72842b6](https://github.com/sendahug/send-hug-backend/commit/72842b6190d3ff70b3ead6795354a178ca77b4e9)).
- The "create post" endpoint was accidentally attempting to access the poster's ID using the back-end key, which caused an error. The key was updated to the front-end key ([772f1d5](https://github.com/sendahug/send-hug-backend/commit/772f1d5c130b803757d7b2f6dddd81e88363302c)).
- Fixed a bug in the "delete filter" endpoint where the word's "ID" (its index in the filtered words array) was treated as a string, which caused the deletion process to throw an error ([5bfbe77](https://github.com/sendahug/send-hug-backend/commit/5bfbe77e24e1e745b51b003c4803c2326a97488a)).

### 2020-06-21

#### Features

- Added an endpoint for updating existing reports ([8e152d1](https://github.com/sendahug/send-hug-backend/commit/8e152d1f88624037ea4d76aa9ac2d76fb32d0e9f)).
- Added an endpoint for creating new reports ([0a6700d](https://github.com/sendahug/send-hug-backend/commit/0a6700d6a4c023c8d2178c2cacbf3be02088e8c8)).
- Added block-related columns to the users' table ([197fb6f](https://github.com/sendahug/send-hug-backend/commit/197fb6f73e47bbf16facac0b5ce3f83e8e14b45c) & [15c3e1e](https://github.com/sendahug/send-hug-backend/commit/15c3e1ed35eecc4cc57c6f15918aa4d1a1e540dc)).
- Added an "open reports" details to users and posts. This includes:
  - Added an "open reports" column to the posts' table and added a filter to the posts' endpoint to ensure reported posts aren't shown to users ([c5ae9c0](https://github.com/sendahug/send-hug-backend/commit/c5ae9c04807d4a971831d503adaf8905b025a4d0) & [3454285](https://github.com/sendahug/send-hug-backend/commit/3454285813bb1ea0849aefe97630d61dd0fd44ae)).
  - Added an "open reports" column to the users' table ([9a12d3b](https://github.com/sendahug/send-hug-backend/commit/9a12d3b030bf6b5139aa6884839ea04737bab1ac)).
  - The "open reports" attribute is now updated when the relevant report is closed ([887757d](https://github.com/sendahug/send-hug-backend/commit/887757de77bd980569206e69b4a2dc7f6e3e02f3)).
- Updated the "update user" endpoint to handle block and unblock data ([9877121](https://github.com/sendahug/send-hug-backend/commit/987712182f5b9f7c2f480aa0c043c91e547aa329) & [944c9f8](https://github.com/sendahug/send-hug-backend/commit/944c9f80da4175631432073aa04e16805a956d61)).
- Added an endpoint for fetching users by type, with initial setup for fetching blocked users ([66f8355](https://github.com/sendahug/send-hug-backend/commit/66f83557d27e383b6e5eaa73ccc3b2b8cd1533e8)).
- Added an initial word filter to filter out words before saving posts/messages. This includes a new word filter module, an endpoint for fetching the filtered out words, an endpoint for adding a word and an endpoint for deleting a word ([ecabcf6](https://github.com/sendahug/send-hug-backend/commit/ecabcf622cec2302dd6a35b8dda890e0668fbfbf) - [b7bf6fb](https://github.com/sendahug/send-hug-backend/commit/b7bf6fb8ce3d27b1527c6dbcdebcf64f43f67365)).

#### Changes

- Deleted the SQLAlchemy relationship between the User and Report tables ([2794ba3](https://github.com/sendahug/send-hug-backend/commit/2794ba30e02fb810e2ca1858bfc7f94307bb45b7)).

#### Fixes

- Added a missing check to ensure an attempt to create a user without an Auth0 ID is prevented. Instead, an error is returned to the user ([dcb848a](https://github.com/sendahug/send-hug-backend/commit/dcb848ad4c58adb58a8ac82c439552cc5215886a)).

### 2020-06-20

#### Features

- Added thea ability to report users and posts. This includes:
  - Added a reports table for saving reports ([43f77a6](https://github.com/sendahug/send-hug-backend/commit/43f77a60ec8e8279dbb521f16395a3b703a07dd1) & [41a0797](https://github.com/sendahug/send-hug-backend/commit/41a07977ea05149c18959092db3722aba9a39417) & [6ddf488](https://github.com/sendahug/send-hug-backend/commit/6ddf488489029f82a049384077869b4486efb81c)).
  - Added the reports' queries to the `joined_query` helper ([5f94920](https://github.com/sendahug/send-hug-backend/commit/5f94920e2c1284614e0f027ffcd1c6f8f98f4703)).
  - Added an endpoint for fetching open reports ([815b006](https://github.com/sendahug/send-hug-backend/commit/815b006fba47b2fa36605267fc5f4482983f3f6a) & [af9ec2a](https://github.com/sendahug/send-hug-backend/commit/af9ec2a2d91e46197ecd1cd3b98f683bffe2f8d4)).

### 2020-06-18

#### Features

- Added an POST "/" endpoint for running a search ([ccbe98b](https://github.com/sendahug/send-hug-backend/commit/ccbe98bbe1c740e9c15d19699a2d121deea44e12)).
- Added a helper method for deleting multiple records from the database ([ea9cf14](https://github.com/sendahug/send-hug-backend/commit/ea9cf1422c9fc46aa4c81ff9b61847410280454f)).
- Added an endpoint for deleting all of a user's posts ([d927007](https://github.com/sendahug/send-hug-backend/commit/d927007198a2b8a8171ba937d62dd7fd466befda) & [3a49c3f](https://github.com/sendahug/send-hug-backend/commit/3a49c3f3039a67d639fc9cc70755327a8c1face1)).
- Added an endpoint for clearing a mailbox ([a38226b](https://github.com/sendahug/send-hug-backend/commit/a38226b20fd76c5d3b64f485b9f600001bf79df9) & [68ff451](https://github.com/sendahug/send-hug-backend/commit/68ff4518e9f986cdaa2d4f751aa57088edc5d88b)).

#### Changes

- Merged the "delete message" and "delete thread" endpoints to create a more RESTful structure ([1b0505a](https://github.com/sendahug/send-hug-backend/commit/1b0505a60195c130bbe5314d6bf3f6b0aab71f99) & [2eaed34](https://github.com/sendahug/send-hug-backend/commit/2eaed34a27c61ab8ba1c0cc291b323702c585db2)).

### 2020-06-17

#### Features

- Added the ability to send someone a hug from their profile via the "edit user" endpoint ([1d967bc](https://github.com/sendahug/send-hug-backend/commit/1d967bc9197e691e18c0bc5a30e33635b0c8acdb)).

#### Fixes

- Added a check to ensure an error is raised in the "edit user" endpoint only if another user is attempting to edit another user's display name. This fixes a bug that caused an error to be thrown when users attempted to send a hug to another user ([d19eb93](https://github.com/sendahug/send-hug-backend/commit/d19eb93deb996702ce06729ac68952aff68e944e)).

### 2020-06-16

#### Changes

- The "get single user" endpoint can now fetch users based on both their Auth0 ID and their internal ID, instead of just based on their Auth0 ID ([a8f67f1](https://github.com/sendahug/send-hug-backend/commit/a8f67f1d7bc34e1ad3a2d8379d9d57520064c3f9)).

### 2020-06-15

#### Documentation

- Updated the link to the main README in the repo's README ([976806a](https://github.com/sendahug/send-hug-backend/commit/976806a03735a426df5513d6af5a2d5bedd9852c)).

### 2020-06-14

#### Features

- Added support for message threads. This includes:
  - Added a `threads` table ([9938fe3](https://github.com/sendahug/send-hug-backend/commit/9938fe3464768a4b9a927e779661aef1f7b56b5b) & [a2aeef4](https://github.com/sendahug/send-hug-backend/commit/a2aeef47b6c19e38fc0b1e8fa981a3f37f9c65a2)).
  - Added the ability to fetch threads in the endpoint for fetching messages ([d33cbe8](https://github.com/sendahug/send-hug-backend/commit/d33cbe8ad90576808f59e279a35a90a6130058ab)).
  - Added the ability to fetch a single thread ([eb177c8](https://github.com/sendahug/send-hug-backend/commit/eb177c8760841b9d0cf1a67814a41417d2afb9f7)).
  - Added the ability to delete threads ([85f6104](https://github.com/sendahug/send-hug-backend/commit/85f6104833674eee78a99f2b265ffbec984400cf) & [dedf637](https://github.com/sendahug/send-hug-backend/commit/dedf637741ac86753ff4ea0b9d2e4370266633b1)).

#### Changes

- A thread ID is now assigned to all new messages. If there's already a thread between the two users, that thread's ID is assigned to the message; otherwise, a new thread is created ([0d80809](https://github.com/sendahug/send-hug-backend/commit/0d80809c8ba4a1d1e0db300fb7b271ca934f725e)).

#### Chores

- Fixed an error in the most recent migration, which caused deployment to fail ([734f1c6](https://github.com/sendahug/send-hug-backend/commit/734f1c6ea3c68325cbf11462f199b4f0a54cea14)).

### 2020-06-12

#### Chores

- Added a gitignore file ([5b47356](https://github.com/sendahug/send-hug-backend/commit/5b473566625be3a7d9ad0a43d353379b459f8dc0) & [652ae86](https://github.com/sendahug/send-hug-backend/commit/652ae86f4387c373de2f9f039bc31606c7088b5b)).

### 2020-06-11

#### Changes

- Moved the Auth0 variables to environment variables ([5ca5243](https://github.com/sendahug/send-hug-backend/commit/5ca5243fea0b32f4a9291b60c9319bbe73d9c4f7)).

#### Documentation

- Updated the names of the environment variables in the README to match the updated names in the code ([73eb189](https://github.com/sendahug/send-hug-backend/commit/73eb189961cdd4b0bf07b4984eab96ac14812b24)).

### 2020-06-10

#### Features

- Added the option to fetch messages in the outbox mailbox ([7794272](https://github.com/sendahug/send-hug-backend/commit/77942720cf01a97097064079bd09999be7a6fb9d)).

#### Changes

- Moved the frontend URL to an environment variable ([4d975d9](https://github.com/sendahug/send-hug-backend/commit/4d975d94165a6bdb091532a73fa04af4f7895a32)).
- Moved the database URL to an environment variable ([b2c6ec5](https://github.com/sendahug/send-hug-backend/commit/b2c6ec5a56fda7ebceef235d7c4024b76f4c7f7c)).

#### Chores

- Added a requirements file with all of the app's requirements ([ae1c73a](https://github.com/sendahug/send-hug-backend/commit/ae1c73ad2055a4700eef4e64fdcb41b7aba519e0) & [e4068f3](https://github.com/sendahug/send-hug-backend/commit/e4068f3db0b6f25b5a2ecdbbd84565a37aceafb8) - [1aafc7e](https://github.com/sendahug/send-hug-backend/commit/1aafc7ee043fa22bc6bf33c53c199b6ac5ec9f92)).
- Added a script to handle database migrations when deploying to Heroku ([85fdf89](https://github.com/sendahug/send-hug-backend/commit/85fdf8959af59c6d35d1979ef17e4722c056fd64)).
- Added a procfile to enable deployment on Heroku ([1f63cd4](https://github.com/sendahug/send-hug-backend/commit/1f63cd4c5034e4f7287cb13d9e124ce06ee02148)).

#### Documentation

- Added curl samples to all endpoints in the API docs ([1de0f6c](https://github.com/sendahug/send-hug-backend/commit/1de0f6c16cfe412f1c5950e03995e0898500c7a3)).
- Added instructions for hosting the app ([16ac166](https://github.com/sendahug/send-hug-backend/commit/16ac1661dc02d9ca1e67e354b1e3b1b956c96646)).

### 2020-06-09

#### Features

- Added environment variables with data relating to the Auth0 setup and the database setup ([3a6a609](https://github.com/sendahug/send-hug-backend/commit/3a6a609e1cbf68f5cd48889827a557e56d419108) & [331520d](https://github.com/sendahug/send-hug-backend/commit/331520d9be9c19ef60e3857ddfd8adcbc8d67422)).
- Added support for user roles. This includes:
  - Added a role column to the users' table ([58bb1aea](https://github.com/sendahug/send-hug-backend/commit/58bb1aea80f586d025486a32b334ad1423d09928)).
  - The "edit user" endpoint now sets the user's roles based on the permissions they have ([018ecb7](https://github.com/sendahug/send-hug-backend/commit/018ecb7100b3afa4b43f10fa0332329febf8aaa5)).

#### Fixes

- Fixed a bug where the permission check always returned "no permission" because the token payload was checked for permission instead of the value of its `permissions` key ([de6fa29](https://github.com/sendahug/send-hug-backend/commit/de6fa2910deab46b6d4a3c31bbd29514dc7e7447)).

#### Chores

- Improved the code documentation with comments describing the functions and the endpoints' required permissions ([df75676](https://github.com/sendahug/send-hug-backend/commit/df7567692f2e4d7b98190dcd7a5a1124b83f507d) & [7ea2781](https://github.com/sendahug/send-hug-backend/commit/7ea2781116b6530a96c218fa19f5f48205a6eedf)).
- Updated the tests database to include user roles ([e3fe11d](https://github.com/sendahug/send-hug-backend/commit/e3fe11dc5f1d938f1fdb8760e103ce6419baac6a)).

#### Documentation

- Updated the README with details about running the API locally ([67d9284](https://github.com/sendahug/send-hug-backend/commit/67d928421ac22146829a5a21da81613d84672653) & [dfa1b7a](https://github.com/sendahug/send-hug-backend/commit/dfa1b7a934b44ee23b27bd86291bb4fe02a8f566)).

### 2020-06-08

#### Features

- Added checks to prevent users from editing other users' display name ([572af99](https://github.com/sendahug/send-hug-backend/commit/572af9953a0cf625628a22b6d171a82c13ad8674)).
- Added checks to prevent users from reading or deleting other users' messages ([f1f25a1](https://github.com/sendahug/send-hug-backend/commit/f1f25a138285eaf590aa1192855430c2f464fc95)).
- Added a check to prevent users from sending a message from another user's account ([0be43f8](https://github.com/sendahug/send-hug-backend/commit/0be43f841f8e6319719c572afcb6b25d338c4d50)).

#### Changes

- Previously, when an ID wasn't provided in endpoints that require an ID (e.g., post ID in the posts' edit endpoint), the app returned a 400 error code. Now, the app returns 404, which is a better fit for the error as there's no item with an ID of 'None' ([4297ac3](https://github.com/sendahug/send-hug-backend/commit/4297ac3d2dabe02c493cdba514b1d6399bdbbe6d)).

#### Fixes

- Fixed an error in the way the currently logged in user is fetched when reading messages, which caused all checks to fail ([778024f](https://github.com/sendahug/send-hug-backend/commit/778024fa03708b1e7c268cda1aebf83367bdfafc)).
- Fixed a bug where having zero messages in an inbox caused an error due to variables that were only defined in one branch of an if/else statement ([a53b1cc](https://github.com/sendahug/send-hug-backend/commit/a53b1cca2c924e4c6b7f3a6eddfaf391e25ce66e)).
- Fixed an error that caused the messages endpoint to return all messages, regardless of which user they're for ([f163a82](https://github.com/sendahug/send-hug-backend/commit/f163a82d888d2feff8d92857f4d023fa002ad98c)).
- Fixed a bug where having only one allowed permission in an endpoint caused the permission checker to error because it was expecting two allowed permissions ([24c88dc](https://github.com/sendahug/send-hug-backend/commit/24c88dcbbfa864afcb141db232ac4a08ba769eaf)).
- Fixed an error in pagination that caused the pagination helper to return one less item than it should've ([5565c9d](https://github.com/sendahug/send-hug-backend/commit/5565c9d0e41a510056b258a877ba585cac593e87)).
- Fixed a bug where attempting to edit a post that doesn't exist caused an error due to an attempt to access the post's writer ([5565c9d](https://github.com/sendahug/send-hug-backend/commit/5565c9d0e41a510056b258a877ba585cac593e87)).

#### Chores

- Added further tests, as well as headers for testing authentication and authorisation ([92a97f7](https://github.com/sendahug/send-hug-backend/commit/92a97f7c35eb676cbed179ff2101f4b9692d1770) - [ac3d13a](https://github.com/sendahug/send-hug-backend/commit/ac3d13a9dc22b979b99620b13ca94afc05ee48c7)).
- Added initial data for testing (in the form of a database dump). ([5a9223c](https://github.com/sendahug/send-hug-backend/commit/5a9223c3cb6e53de01a457e3c175ec0abae27bd9) - [d74a9f5](https://github.com/sendahug/send-hug-backend/commit/d74a9f5cfbdf4e2a23af7ada1903fdda79925799))
- Fixed various bugs in tests ([f7f8beb](https://github.com/sendahug/send-hug-backend/commit/f7f8bebfdbc4f5ffa2b9e1bffecae98936aabec6) & [fcf3a5b](https://github.com/sendahug/send-hug-backend/commit/fcf3a5b5f445d8a4c289a9ae3836f4c685f4fc66) & [496dbfb](https://github.com/sendahug/send-hug-backend/commit/496dbfbe069192d6539724aa0c0fdd1b73693fa6)).

### 2020-06-07

#### Changes

- Adjusted the code responsible for decoding the JWT to fail gracefully if an invalid token is passed in, instead of just throwing an internal error that doesn't reach the front-end ([eaac000](https://github.com/sendahug/send-hug-backend/commit/eaac0004b87d2aeaac699b8ad13076e77df41410)).

#### Chores

- Added unittest and started setting up unit tests for the project ([12aa04c](https://github.com/sendahug/send-hug-backend/commit/12aa04c18f5d43924bec37293a7e22d711b38814) - [9105bb7](https://github.com/sendahug/send-hug-backend/commit/9105bb73c0a0660eee08f86422017d7731229b3e)).

#### Documentation

- Added testing instructions to the README ([f09fefb](https://github.com/sendahug/send-hug-backend/commit/f09fefb55c81386246c0ebee83f1bf7d7e798467)).

### 2020-06-05

#### Changes

- Consolidated posts/new and posts/suggested to one endpoint for fetching posts by type ([6cfa7e0](https://github.com/sendahug/send-hug-backend/commit/6cfa7e0cf9855e53b84766a63ccd5be9290f7a9a)).

#### Documentation

- Added authentication details to the README ([38cd30a](https://github.com/sendahug/send-hug-backend/commit/38cd30a4be21a1860c9b22924d2615f2ff4c8550)).

### 2020-06-04

#### Fixes

- The "total pages" value returned by endpoints with pagination is now correctly rounded up. This fixes a bug where the total pages number wasn't an integer and was displayed as such to the user ([8c49bba](https://github.com/sendahug/send-hug-backend/commit/8c49bbafa25e5ea5fd40da8521cbd01869a8a41b)).
- Added a missing alias in the messages' endpoint's SQL. Previously, the same table was joined twice without an alias, which caused the whole statement to fail ([47f61a0](https://github.com/sendahug/send-hug-backend/commit/47f61a0d77c746f26a2b1c3e61b41b125827604e)).

#### Documentation

- Updated the API documentation with details about the new endpoints ([41478d6](https://github.com/sendahug/send-hug-backend/commit/41478d642b8ae11ca3a36018d9a4a8e30bc82a86)).

### 2020-06-03

#### Features

- Added support for pagination in all "read all" endpoints ([9bfa525](https://github.com/sendahug/send-hug-backend/commit/9bfa52588c9d39f731a1cf28272dd8111a607e5e)).
- Added the ability to update the user's display name ([7a37c12](https://github.com/sendahug/send-hug-backend/commit/7a37c1203dcb28302607c7a8d229ba17490febd7)).
- Added new endpoints for fetching all posts of a certain type (suggested and recent). ([e1c2e0d](https://github.com/sendahug/send-hug-backend/commit/e1c2e0d15f3ea53ff5035e2deccf7d96cff786da))

#### Changes

- The user ID is now a route parameter in the "read one user" route, instead of a query parameter ([55ea6a4](https://github.com/sendahug/send-hug-backend/commit/55ea6a4148707173f64457d0cbb5099919783773)).

### 2020-06-02

#### Features

- Added an error handler for 405 errors ([e1caca8](https://github.com/sendahug/send-hug-backend/commit/e1caca8164b48b67d3af0b800d6d042bb3de95ff)).

#### Changes

- Deleted an unnecessary update to the number of posts a user posted in the users' update endpoint ([5a473db](https://github.com/sendahug/send-hug-backend/commit/5a473dba8b26f17e563bfa2021e74bc2b89817a7)).
- New posts are now sorted by date when fetching posts ([93f3008](https://github.com/sendahug/send-hug-backend/commit/93f30082f2a209074974571411c6e358e48eb328)).

#### Fixes

- The posts' edit endpoint was accidentally trying to access JSON keys using a dot notation instead of the correct dictionary notation. This was updated to the correct access method ([93f3008](https://github.com/sendahug/send-hug-backend/commit/93f30082f2a209074974571411c6e358e48eb328)).
- Added missing session commit to the helper method for deleting rows from the database ([93f3008](https://github.com/sendahug/send-hug-backend/commit/93f30082f2a209074974571411c6e358e48eb328)).
- The "add message" endpoint was trying to access the message's text using the wrong key. This was updated to the correct key ([94a7880](https://github.com/sendahug/send-hug-backend/commit/94a78803bbf5f8b868fb1f6117af829b035b5c61)).

### 2020-06-01

#### Features

- The database helper methods now return the formatted JSON for the objects added/updated, instead of the SQLAlchemy objects ([592426a](https://github.com/sendahug/send-hug-backend/commit/592426a75da972041952583c4f62c962fdf30902)).

#### Changes

- Moved any query that joined multiple tables together (e.g., main page queries) to a helper method for "joined queries" ([5b596b6](https://github.com/sendahug/send-hug-backend/commit/5b596b6d82f393c1ed29b4c7ab8eb395b25e79c2)).

#### Fixes

- Fixed attribute references in POST /post endpoint. The endpoint previously tried accessing the JSON keys based on the names of the columns in SQLAlchemy instead of the keys based on the names set in the front-end. The keys' names were updated to match the incoming request from the front-end ([c151f15](https://github.com/sendahug/send-hug-backend/commit/c151f15de3239d446f40e5e132a0a1dd83bf1d65)).

### 2020-05-31

#### Features

- Added an endpoint for fetching a user's posts ([3f887dc](https://github.com/sendahug/send-hug-backend/commit/3f887dc62327ff7623d61b0faca7850a2beed053)).
- Improved the error handling for "no user ID" in endpoints where user ID is required ([07ec306](https://github.com/sendahug/send-hug-backend/commit/07ec306397f2324e44c939e78afc6b154c488953)).
- Added a check before the messages' table join to ensure there are messages ([76c69ff](https://github.com/sendahug/send-hug-backend/commit/76c69ffd9687b43c2726fb8aeec1b7ca03c8044d)).

#### Fixes

- Fixed reference errors in the 'create user' endpoint and in the JWT handling ([7b8d539](https://github.com/sendahug/send-hug-backend/commit/7b8d53985f692604d8dbea6192bedbf045f41c5f)).
- The user data in the 'edit user' endpoint was accidentally treated as an object (with properties accessed using the `.` notation) instead of a dictionary, which caused a reference error. This was updated to the correct notation ([0cab697](https://github.com/sendahug/send-hug-backend/commit/0cab69713afbd2ff6499d66498d49ee7c401cb0c)).
- Fixed an error when trying to get the number of posts published by a user ([4dfd3d3](https://github.com/sendahug/send-hug-backend/commit/4dfd3d3f0aa8c57c0d78d5755867d6af9f6c5021)).

#### Documentation

- Updated the README with more details about files and dependencies ([bbb7274](https://github.com/sendahug/send-hug-backend/commit/bbb727434b6a805910b90f281cd3c7ce2ef1d389) & [33cdb8c](https://github.com/sendahug/send-hug-backend/commit/33cdb8c392292c45ee40966bdd126f634e0088e0)).

### 2020-05-30

#### Features

- Added a login counter to the users table to track the number of times a user logs in ([702fcb0](https://github.com/sendahug/send-hug-backend/commit/702fcb0eabbb48ea64d211fb98f3944275f00e73) & [5c203d6](https://github.com/sendahug/send-hug-backend/commit/5c203d6c4d6c988c7546009b9842dc2fc544e509)).

#### Fixes

- Fixed a duplicate headers error in the CORS configuration ([ebac524](https://github.com/sendahug/send-hug-backend/commit/ebac5245df3034c938f12e98ee3b3bda5bf8004d)).

### 2020-05-29

#### Fixes

- Fixed a reference error in the requires_auth decorator ([0b57af6](https://github.com/sendahug/send-hug-backend/commit/0b57af61177928b3f1c4b14c0b258bf2bfcd8133)).

### 2020-05-28

#### Features

- Added authorisation handling. The authentication header now also checks for whether the user has the required permission to access a given endpoint ([51d55bb](https://github.com/sendahug/send-hug-backend/commit/51d55bb6d58aa1c1909f68a70d7ae2b412a66d45) - [0b7b86d](https://github.com/sendahug/send-hug-backend/commit/0b7b86d2a23375f3d6b0b0731c82a8640393eeb7)).
- The app's endpoints (except the home route) now require the relevant permission (e.g., `post:post` in POST /posts) to access ([5c63371](https://github.com/sendahug/send-hug-backend/commit/5c63371b7e84dd5f81b8c8043a5266106ac40daf)).
- When attempting to edit or delete posts, the app now checks whether the user is trying to change their own post or whether they have permission to change any post before allowing the edit/delete ([1907be4](https://github.com/sendahug/send-hug-backend/commit/1907be4c25060d0213e7f29b85fa6c735d36dba5) & [5d7f70e](https://github.com/sendahug/send-hug-backend/commit/5d7f70e9b71d55560f47a1c6f0df06b203102396)).

### 2020-05-27

#### Features

- The user endpoints now require a valid JWT to access them ([1d4d89e](https://github.com/sendahug/send-hug-backend/commit/1d4d89e2280009542e095e2de0e026044f3e13a9)).
- Added a check to ensure users aren't created twice and a handler for 409 errors ([db53332](https://github.com/sendahug/send-hug-backend/commit/db533326502dc3bd831d59b81dd76f7abc8dc0bf)).

#### Changes

- The parameters in the users' creation endpoint were changed to match the updated model ([313e412](https://github.com/sendahug/send-hug-backend/commit/313e412983bc51678ac39a20053e096076cec0e1)).

### 2020-05-26

#### Features

- Added support for user authentication ([b937e64](https://github.com/sendahug/send-hug-backend/commit/b937e642083b19a5a269bba0d8976b6fea280bd4) - [9a79090](https://github.com/sendahug/send-hug-backend/commit/9a7909067eb22396b551a8e0e206e6ad56915aa4)). This includes:
  - An error for authentation/authorisation issues.
  - A function for checking the authorisation header.
  - A function for checking the validity of a JWT.
  - A decorator for handling authentication in the endpoints.
- Added a display name column to the users table ([d90db03](https://github.com/sendahug/send-hug-backend/commit/d90db03051d980ec78dacecc1ba9aa67338af444)).

#### Fixes

- The front-end's URL in development was accidentally set to the back-end's URL, which meant all requests from the front-end resulted in a CORS error. The URL was updated to the correct front-end URL ([f23c8ca](https://github.com/sendahug/send-hug-backend/commit/f23c8caf6a558f492f7c87877acb1ae8bbb0a032)).

### 2020-05-24

#### Documentation

- Added an API documentation file with details about all the existing endpoints ([73eb458](https://github.com/sendahug/send-hug-backend/commit/73eb458afdf7c307e841165b62204d91e164ddac)).

### 2020-05-23

#### Features

- Added a PATCH endpoint for editing posts ([bc803d8](https://github.com/sendahug/send-hug-backend/commit/bc803d8740ab8d60265083df217f134518e2bb55)).
- Added a PATCH endpoint for editing users ([decfc21](https://github.com/sendahug/send-hug-backend/commit/decfc2145121336353d4ed2f69643ed151a3dcac)).

#### Fixes

- Fixed a bug where the posts' edit endpoint attempted to return the SQLAlchemy object instead of a formatted dictionary, which caused an error (as the objects aren't JSON-serializable). ([9d3a8fc](https://github.com/sendahug/send-hug-backend/commit/9d3a8fc0a9859278a323f24279de323efdd35c61))

### 2020-05-21

#### Fixes

- Added previously-missing keys to the models' `format` methods to ensure all the required columns are added to the objects the API returns ([721a034](https://github.com/sendahug/send-hug-backend/commit/721a03467ecde82bec595e66b1458e75f29ae891)).

### 2020-05-20

#### Features

- Added an endpoint for fetching a single user's data ([4742c8e](https://github.com/sendahug/send-hug-backend/commit/4742c8e6bd1e634991b0ea3cd9c08cac7b58e97a)).
- Added an endpoint for fetching a user's messages ([ae69245](https://github.com/sendahug/send-hug-backend/commit/ae69245f11a3c8769c39ef8415b514ea1269e28f)).
- Added a 'username' column to the users table ([e0b2d45](https://github.com/sendahug/send-hug-backend/commit/e0b2d45ff392495b055a1a5d23da8aa6ffdc949e)).
- Added an error handler for 404 error ([606f3b7](https://github.com/sendahug/send-hug-backend/commit/606f3b73eb60b0a170119c219af079d3fdd39f67)).
- Added helper methods for adding, updating and deleting objects from the database ([5a92834](https://github.com/sendahug/send-hug-backend/commit/5a92834ff99f272275b63fdd6624427c0e8a263a)).
- Added POST endpoints for creating posts, users and messages ([0d6dcb6](https://github.com/sendahug/send-hug-backend/commit/0d6dcb6d9f7330dc07a251a4a9255f35ff304497)).
- Added error handlers for 400, 422 and 500 errors ([3b05246](https://github.com/sendahug/send-hug-backend/commit/3b0524696fb6b43b1236a78e6d2534f5935f9977)).
- Added DELETE endpoints for deleting posts and messages ([87f35d9](https://github.com/sendahug/send-hug-backend/commit/87f35d98c1f880e1b76569be67b0537f00b2a42e)).

#### Fixes

- Fixed bugs in user-related endpoints, which broken when a user ID wasn't provided ([8a702ac](https://github.com/sendahug/send-hug-backend/commit/8a702acaebb8bdd64afd5c1ff73b4000677cca7c)).

### 2020-05-19

#### Features

- Added initial SQLAlchemy models for posts, users and messages ([499f432](https://github.com/sendahug/send-hug-backend/commit/499f432961434741e92c1ef78081591ad7c91144)).
- Set up Flask-CORS to enable communication with the front-end ([771ebde](https://github.com/sendahug/send-hug-backend/commit/771ebdeee2f192d96c6d673cd9f1cb1fe10e34ba)).
- Added the database initialisation to the app's creation process ([b165d83](https://github.com/sendahug/send-hug-backend/commit/b165d837f431b79233768b99a59491bf016af84a)).
- Instantiated Flask-Migrate and created the initial migration ([b471339](https://github.com/sendahug/send-hug-backend/commit/b471339f29cafb8533a1275021126654b3bec52e) & [ae48e72](https://github.com/sendahug/send-hug-backend/commit/ae48e72c3fba162609643866a6d55227b4f05131)).
- Added date columns to the posts and messages tables ([8207ca0](https://github.com/sendahug/send-hug-backend/commit/8207ca07c6bad77941af6073fe49427dfd32d731)).
- Added initial helper methods for formatting data to JSON to each model ([51e38df](https://github.com/sendahug/send-hug-backend/commit/51e38dfd073c2946833f3d755f5043e0e4a70756)).
- Added an initial home endpoint ([7bdbdf3](https://github.com/sendahug/send-hug-backend/commit/7bdbdf363dcaf7b0b4728f8991ee2b190e327c6c)).
- Added a 'hugs' columns to the posts table ([f3b9bfc](https://github.com/sendahug/send-hug-backend/commit/f3b9bfc61e7aa7bfa2656cf5c2f3b6f6aafc081a)).

### 2020-05-14

#### Documentation

- Added an initial README ([e271602](https://github.com/sendahug/send-hug-backend/commit/e271602215d8fa19c909803f76ab7a8ad9227719)).

### 2020-05-13

#### Features

- Initialised the project with a basic Flask app ([f50cc09](https://github.com/sendahug/send-hug-backend/commit/f50cc09858a48e020b8cc4786298c293f5781d16)).
