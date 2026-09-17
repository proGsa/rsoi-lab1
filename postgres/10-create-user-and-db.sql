-- file: 10-create-user-and-db.sql
CREATE DATABASE persons;
CREATE ROLE program WITH LOGIN PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE persons TO program;
ALTER ROLE program WITH LOGIN;