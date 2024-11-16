CREATE DATABASE test_sah;
-- plaintext password is fine here as the test database is only hosted locally
CREATE USER test_sah WITH ENCRYPTED PASSWORD 'test1test2test3test4';
GRANT ALL PRIVILEGES ON DATABASE test_sah TO test_sah;
\c test_sah
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_sah;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_sah;
GRANT ALL ON SCHEMA public TO test_sah;
