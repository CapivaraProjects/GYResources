CREATE TABLE TEXTS (
   id SERIAL PRIMARY KEY,
   language VARCHAR(20),
   tag VARCHAR(2000),
   value VARCHAR(100000),
   description VARCHAR(2000)
);

CREATE TABLE USERS (
   id SERIAL PRIMARY KEY,
   id_type SERIAL,
   email VARCHAR(200),
   username VARCHAR(20),
   password VARCHAR(128),
   salt VARCHAR(32),
   date_insertion VARCHAR(100),
   date_last_update VARCHAR(100)
);