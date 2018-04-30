CREATE DATABASE bot
  WITH OWNER = bot
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'Russian_Russia.1251'
       LC_CTYPE = 'Russian_Russia.1251'
       CONNECTION LIMIT = -1;

CREATE TABLE organizations
(
  id serial,
  organization character(80),
  faculty character(80),
  studgroup character(20),
  tag character(31)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE organizations
  OWNER TO bot;

CREATE INDEX trgm_idx
  ON organizations
  USING gin
  (lower((((organization::text || ' '::text) || faculty::text) || ' '::text) || studgroup::text) COLLATE pg_catalog."default" gin_trgm_ops);

CREATE TABLE reports
(
  type character(2),
  report_id serial,
  user_id integer,
  report text,
  date date
)
WITH (
  OIDS=FALSE
);
ALTER TABLE reports
  OWNER TO bot;

CREATE TABLE schedule
(
  id serial,
  tag character(31),
  day character(10),
  "number" smallint,
  type smallint,
  "startTime" time without time zone,
  "endTime" time without time zone,
  title character(100),
  classroom character(20),
  lecturer character(50)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE schedule
  OWNER TO bot;

CREATE TABLE users
(
  type character(2),
  id integer,
  name character(30),
  username character(30),
  "scheduleTag" character(31),
  auto_posting_time time without time zone,
  is_today boolean
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users
  OWNER TO bot;
