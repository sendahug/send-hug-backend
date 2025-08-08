#!/bin/bash

# script to setup local dev and test databases
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dev_db_password>"
    exit 1
fi

echo Creating dev db creds
mkdir -p .secrets/db_development_creds
sed -e "s/<INSERT_PW_HERE>/$1/" .secrets/db_creds.json.example > .secrets/db_development_creds/latest.json
echo Creating test db creds
mkdir -p .secrets/db_test_creds
sed -e "s/sendahug/test_sah/" -e "s/sah_api_user/test_sah/" -e "s/<INSERT_PW_HERE>/$1/" \
  .secrets/db_creds.json.example > .secrets/db_test_creds/latest.json

echo Creating dev db
sed -e "s/<INSERT_PW_HERE>/$1/" init_dbs.sql | sudo -u postgres psql
echo Creating test db
sed -e "s/sendahug/test_sah/" -e "s/sah_api_user/test_sah/" -e "s/<INSERT_PW_HERE>/$1/" \
  init_dbs.sql | sudo -u postgres psql
