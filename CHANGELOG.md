# Changelog

## Unreleased

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

#### Chores

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

#### Chores

- Migrated the tests from unittest to Pytest, which will allow us to split the tests according to the test subject, move the dummy data into fixtures which are reset automatically after every test, and parameterise tests to reduce duplicate code ([c0ca9ec](https://github.com/sendahug/send-hug-backend/commit/c0ca9ec3f07748937a80731d0438cefe385f72db) - [dd29135](https://github.com/sendahug/send-hug-backend/commit/dd29135d6ef8d760d49aaf5f3a42d249081122be)).

#### Documentation

- Adjusted the testing instructions in the README ([27f0297](https://github.com/sendahug/send-hug-backend/commit/27f029712c56cd94a9d6ac497a0400d0ceaabc7c)).

### 2023-02-25

#### Changes

- Split filter fetching from wordfilter check. While the word filter needs the "bad" words to filter out, it shouldn't be fetching them. Instead, they should be fetched in the context of the app and then passed into the filter. ([4e8636c](https://github.com/sendahug/send-hug-backend/commit/4e8636cb1f8987d8c62e3a16fff9e74d1637415a))
- Deleted unneeded checks for path params. Path parameters' existence checks are handled by Flask, so there's no need to validate that they exist manually. ([30717b9](https://github.com/sendahug/send-hug-backend/commit/30717b9afa48b4762f5d802a5990621ff8341429))

#### Chores

- Added further tests ([ffa2421](https://github.com/sendahug/send-hug-backend/commit/ffa242149e3a6034127d46c0b6c73d342fde4102)).

### 2023-02-12

#### Features

- Added a helper method for bulk inserts/updates ([8f522ee](https://github.com/sendahug/send-hug-backend/commit/8f522ee316b512b98b80f80b235e07fb93280763) & [fff806b](https://github.com/sendahug/send-hug-backend/commit/fff806b47394e1500b6c93c716c9cecd7b70311e)).
- Added on-delete/on-update rules to various foreign keys ([427e68e](https://github.com/sendahug/send-hug-backend/commit/427e68e3a598089272a5e48cab9a1d323f23e88a)).

#### Changes

- Moved the database-related error handling from the various endpoints to the relevant database helper functions. It doesn't really make sense to be doing the same error handling in multiple places when it's all related to the database. This also allows handling DBAPI errors related to bad data with the correct error code. ([7614d66](https://github.com/sendahug/send-hug-backend/commit/7614d669a20381b2dcf27c6f7bd4d463a6e342bd))
- Updated the multiple-users update in GET /users to use the new bulk update helper function ([2273bbf](https://github.com/sendahug/send-hug-backend/commit/2273bbfb54eaf054d8a57af904fec15b826dd5bd)).

#### Chores

- Replaced the methods' documentation with python docstrings ([d56ea87](https://github.com/sendahug/send-hug-backend/commit/d56ea875a77d40b4693772c34da6966909b650fc)).
- Added tests for more helper functions and fixed some tests' data ([4218a98](https://github.com/sendahug/send-hug-backend/commit/4218a9870d5a6dd30f64200b16c6e38faabe6fac) - [760a00a](https://github.com/sendahug/send-hug-backend/commit/760a00a3c99c581ac27f0cdf898fdb85c45a6e78)).

### 2023-02-11

#### Changes

- Replaced all `print` calls with logging to a proper python logger ([46e58f3](https://github.com/sendahug/send-hug-backend/commit/46e58f35ddaae56b4eeaf28f408dfe37b3e8fbb6)).
- Standardised the db helpers' responses to avoid confusion in the endpoints ([82065f0](https://github.com/sendahug/send-hug-backend/commit/82065f0b38d5afad81327a642665d5a98aeae4a2)).

#### Chores

- Fixed the typing in various parts of the app ([3ba34e6](https://github.com/sendahug/send-hug-backend/commit/3ba34e6d812dd567c34d26f334ef8d1ec23af9a5) - [f51612d](https://github.com/sendahug/send-hug-backend/commit/f51612dc6a9e693d5878bed5c240cd8850e56f14)).

### 2023-02-06

#### Chores

- Deleted an unneeded install step in CI ([ebec08e](https://github.com/sendahug/send-hug-backend/commit/ebec08e1376f5b8181cf8f6928c5a79262800070)).

### 2023-02-05

#### Features

- Added a new helper method for validating post/message texts ([449281a](https://github.com/sendahug/send-hug-backend/commit/449281a137c2ad8f5cac3d32a8cb5aaa8ad9de52)).

#### Chores

- Cleaned up more old code. This includes improved typing, simplified nested statements, and the removal of duplicate code ([c46c702](https://github.com/sendahug/send-hug-backend/commit/c46c7028cc43bb61e832535e0d4b4315654c0ca6) - [4065d5b](https://github.com/sendahug/send-hug-backend/commit/4065d5b9e9405bee268a12c0064179ee7d573d79)).

### 2023-01-31

#### Chores

- Added more tests for the app utilities ([001722b](https://github.com/sendahug/send-hug-backend/commit/001722bad1c799ef145cfefce4495448cb4b2991)).

### 2023-01-29

#### Changes

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

#### Changes

- Moved the filter and validator utilities to a new `utils` directory ([0105450](https://github.com/sendahug/send-hug-backend/commit/0105450a5e05ab76741cb15c895c6a99739f2b97)).
- Moved the database helper functions from the models' module to a new database-related module ([10bf93b](https://github.com/sendahug/send-hug-backend/commit/10bf93bec16d4804d21b776d7bb20475cf30fe3f)).
- Adjusted the way Flask-SQLAlchemy is initialised to correctly pass in the required settings ([f5851af](https://github.com/sendahug/send-hug-backend/commit/f5851afca5e7d3b007174e4747defe7be6b624ce) & [d2af058](https://github.com/sendahug/send-hug-backend/commit/d2af058990de28973fa446981d3e06a1fe684b59)).

#### Chores

- Simplified old code in the Validator ([2aa458a](https://github.com/sendahug/send-hug-backend/commit/2aa458a61a3e9ea461d455d702916903a384965c)).
- Deleted the unneeded PyOpenSSL dependency ([bdeeced](https://github.com/sendahug/send-hug-backend/commit/bdeeced78b40d8bd22a7dc0fff10a7c1e00789c2)).
- Added missing copyright notice ([d06ffee](https://github.com/sendahug/send-hug-backend/commit/d06ffee8bea03c69013334dd5be18699e4f5d1b5)).

### 2022-12-19

#### Changes

- Moved the push notifications' helper functions to their own module ([29b5a4f](https://github.com/sendahug/send-hug-backend/commit/29b5a4fa0b28e5eb1be1496625451e4e957c8229)).

#### Chores

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

#### Documentation

- Deleted the pyup badges from the README as they've switched to priced tiers only and those badges weren't particularly useful anyway ([0383362](https://github.com/sendahug/send-hug-backend/commit/038336206c9e16b82712d7d303a814ad4338eb77)).

### 2022-07-24

#### Chores

- Updated the Python runtime version in deployment ([ed2a9d4](https://github.com/sendahug/send-hug-backend/commit/ed2a9d4d6f6549fe0bd83fbbb8225e7182e75456)).

### 2022-06-19

#### Chores

- - Added a funding.yml file to enable sponsoring the team ([ae3d4db](https://github.com/sendahug/send-hug-backend/commit/ae3d4db96c57643f7db4e443bad5bca2ce128498)).

### 2022-06-18

#### Fixes

- Fixed a bug where endpoints handling user data returned an error due to an attempt to use `json.load` on a null value ([959e21a](https://github.com/sendahug/send-hug-backend/commit/959e21ab3854707bf3cc5ea6df26e1a7c692b5c8)).

### 2022-06-12

#### Changes

- Deleted the `manage.py` file, which was previously used to run migrations in deployment ([7ac21d1](https://github.com/sendahug/send-hug-backend/commit/7ac21d1f3fe968c903ecabe9e26798953d9c8844)).

#### Chores

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

#### Features

- Added the users' icon data to the messages' endpoints to allow displaying the icons in the messaging views ([d831d53](https://github.com/sendahug/send-hug-backend/commit/d831d5327ab481d12bcb2def276e141e7a34d4f3)).

#### Fixes

- Renamed the keys in the icon colours' dictionary to match the expected keys in the front-end ([5826418](https://github.com/sendahug/send-hug-backend/commit/5826418335d32939f198d80daeee9492c87030df)).

#### Chores

- Updated the tests and the tests' data to include the new icon data ([717c383](https://github.com/sendahug/send-hug-backend/commit/717c38314bea793da4ad2e5fab66c15249c94c1a) & [b08fc76](https://github.com/sendahug/send-hug-backend/commit/b08fc76f662d6f5baef9db4ba3bec30ea90a3ca5))

### 2020-12-21

#### Fixes

- Fixed a string formatting error in the users' update endpoint ([eb351fd](https://github.com/sendahug/send-hug-backend/commit/eb351fdffe40798f85c48fc6333df87397e40798)).
- The default colours for the users' icons were set to the wrong values. They've now been updated to the correct values ([2088b42](https://github.com/sendahug/send-hug-backend/commit/2088b4295840d7c89cd46ecf5d39cb79e594f25d)).

### 2020-12-20

#### Features

- Added selected icon and icon colours columns to the users table to allow users to select an icon and its colours ([861fe99](https://github.com/sendahug/send-hug-backend/commit/861fe9945caacf69482e639870e3bbf990d2afce) & [041a0ac](https://github.com/sendahug/send-hug-backend/commit/041a0ac7886b0f51ad744a6d2dfd7fa5b1e70a9b)).
- Added the ability to update a user's icon and selected colours in the users' update endpoint ([a81e09a](https://github.com/sendahug/send-hug-backend/commit/a81e09a7fd09081dad64c42b7ec366d1f716e1d8)).

#### Chores

- Updated the test databases ([8c38c0e](https://github.com/sendahug/send-hug-backend/commit/8c38c0ecd2b28c546708e795e7dff82d55fe218e)).

### 2020-12-16

#### Chores

- Adjusted the GitHub Actions workflow and the CircleCI workflow to allow running tests only on pull requests made against the development and the live branches - based on an API request to the CircleCI API - or on commits pushed to either of those branches - based on the CircleCI config ([5426ed6](https://github.com/sendahug/send-hug-backend/commit/5426ed6d88f210b79b18f8d9c3e4fe793fc4db0f) - [24d60e7](https://github.com/sendahug/send-hug-backend/commit/24d60e78a1fbc36632dce179e984a93172aaaf63)).

### 2020-12-15

#### Chores

- Added an initial GitHub Actions workflow to trigger CircleCI builds ([a6aadda](https://github.com/sendahug/send-hug-backend/commit/a6aadda23bbbbe67156f8b0db5eda55d8ac85387)).

### 2020-12-08

#### Chores

- Set the CircleCI workflow to only run on specific branches ([b9ecca0](https://github.com/sendahug/send-hug-backend/commit/b9ecca0bad28cbb3b6b31c048b2d300251aff391)).

#### Documentation

- Replaced the Travis CI bradge in the readme with a CircleCI badge ([47354a2](https://github.com/sendahug/send-hug-backend/commit/47354a2a11321789b37bc3d31d969c64702ea307)).

### 2020-12-07

#### Chores

- Replaced the Travis CI config with a new CircleCI workflow ([fd8032d](https://github.com/sendahug/send-hug-backend/commit/fd8032d8b6bccf4ec0e64d37b7494421569b3341) - [a370cf6](https://github.com/sendahug/send-hug-backend/commit/a370cf68b9e6fd39dfe87ed05164e51c795722be)).

### 2020-12-06

#### Chores

- Added an initial CircleCI workflow file to run tests in CI ([f7d05fd](https://github.com/sendahug/send-hug-backend/commit/f7d05fdff661cbe751ec3f224eee22114b2a2b8c) - [72a2906](https://github.com/sendahug/send-hug-backend/commit/72a2906b4023166aacf0668b0bd6793a4e980399)).

### 2020-11-29

#### Chores

- Changed the create-release workflow to remove the branch restriction as a temporary workaround for it ([e1589fe](https://github.com/sendahug/send-hug-backend/commit/e1589fece668b1eabc9f799e54bc81a37078e366)).

### 2020-11-11

#### Chores

- Added a pyup config file ([4caa558](https://github.com/sendahug/send-hug-backend/commit/4caa55820b695b93aa1ec7b807f45b9d6402d390)).

### 2020-11-08

#### Changes

- Suggested posts are now sorted by date as well as hugs ([7b1c5fe](https://github.com/sendahug/send-hug-backend/commit/7b1c5fe9e4e2740e17ef76edca3c0cddad5da490)).

## v1.0.0 Beta 1
