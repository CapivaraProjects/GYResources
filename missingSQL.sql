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
   password VARCHAR(2000),
   salt VARCHAR(32),
   date_insertion VARCHAR(100),
   date_last_update VARCHAR(100)
);

CREATE TABLE ANALYSIS (
    id SERIAL NOT NULL,
    id_image SERIAL
);

CREATE TABLE ANALYSIS_RESULT (
    id SERIAL NOT NULL,
    id_analysis SERIAL,
    id_disease SERIAL,
    score DECIMAL(10,6)
);
