# Changelog

## Unreleased



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

## v1.0.0 Beta 1
