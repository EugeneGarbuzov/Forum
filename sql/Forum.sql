CREATE TABLE roles (
  id          NUMBER        NOT NULL PRIMARY KEY,
  name        VARCHAR2(30)  NOT NULL,
  description VARCHAR2(200) NOT NULL,
  UNIQUE (name)
);

CREATE SEQUENCE roles_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER roles_trigger
BEFORE INSERT ON roles
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT roles_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /


CREATE TABLE ranks (
  id           NUMBER       NOT NULL PRIMARY KEY,
  name         VARCHAR2(30) NOT NULL,
  bonus_rating NUMBER       NOT NULL,
  UNIQUE (id, name)
);

CREATE SEQUENCE ranks_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER ranks_trigger
BEFORE INSERT ON ranks
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT ranks_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE trophies (
  id   NUMBER       NOT NULL PRIMARY KEY,
  name VARCHAR2(30) NOT NULL,
  UNIQUE (name)
);

CREATE SEQUENCE trophies_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER trophies_trigger
BEFORE INSERT ON trophies
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT trophies_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE tags (
  id   NUMBER       NOT NULL PRIMARY KEY,
  name VARCHAR2(30) NOT NULL,
  UNIQUE (name)
);

CREATE SEQUENCE tags_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER tags_trigger
BEFORE INSERT ON tags
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT tags_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE users (
  id        NUMBER       NOT NULL PRIMARY KEY,
  role_id   NUMBER       NOT NULL,
  rank_id   NUMBER       NOT NULL,
  username  VARCHAR2(30) NOT NULL,
  password  VARCHAR2(30) NOT NULL,
  email     VARCHAR2(30) NOT NULL,
  nickname  VARCHAR2(30) NOT NULL,
  full_name VARCHAR2(30) NOT NULL,
  join_date DATE         NOT NULL,
  status    VARCHAR2(30) NOT NULL,
  signature VARCHAR2(50) NOT NULL,
  FOREIGN KEY (role_id)
  REFERENCES roles (id),
  FOREIGN KEY (rank_id)
  REFERENCES ranks (id),
  UNIQUE (username, email)
);

CREATE SEQUENCE users_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER users_trigger
BEFORE INSERT ON users
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT users_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE journal (
  id          NUMBER        NOT NULL PRIMARY KEY,
  user_id     NUMBER        NOT NULL,
  description VARCHAR2(200) NOT NULL,
  entry_date  DATE          NOT NULL,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);

CREATE SEQUENCE journal_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER journal_trigger
BEFORE INSERT ON journal
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT journal_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE sections (
  id          NUMBER       NOT NULL PRIMARY KEY,
  role_id     NUMBER       NOT NULL,
  name        VARCHAR2(30) NOT NULL UNIQUE,
  create_date DATE         NOT NULL,
  description VARCHAR2(30) NOT NULL,
  FOREIGN KEY (role_id)
  REFERENCES roles (id)
);

CREATE SEQUENCE sections_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER sections_trigger
BEFORE INSERT ON sections
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT sections_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /


CREATE TABLE topics (
  id          NUMBER       NOT NULL PRIMARY KEY,
  user_id     NUMBER       NOT NULL,
  section_id  NUMBER       NOT NULL,
  name        VARCHAR2(30) NOT NULL UNIQUE,
  create_date DATE         NOT NULL,
  description VARCHAR2(30) NOT NULL,
  FOREIGN KEY (section_id)
  REFERENCES sections (id)
  ON DELETE CASCADE,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);

CREATE SEQUENCE topics_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER topics_trigger
BEFORE INSERT ON topics
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT topics_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE messages (
  id          NUMBER        NOT NULL PRIMARY KEY,
  user_id     NUMBER        NOT NULL,
  topic_id    NUMBER        NOT NULL,
  create_date DATE          NOT NULL,
  text        VARCHAR2(400) NOT NULL,
  rating      NUMBER        NOT NULL,
  FOREIGN KEY (topic_id)
  REFERENCES topics (id)
  ON DELETE CASCADE,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);

CREATE SEQUENCE messages_increment
START WITH 1
INCREMENT BY 1
NOMAXVALUE;

CREATE OR REPLACE TRIGGER messages_trigger
BEFORE INSERT ON messages
FOR EACH ROW
WHEN (new.id IS NULL)
  BEGIN
    SELECT messages_increment.nextval
    INTO :new.id
    FROM dual;
  END;
  /

CREATE TABLE trophies_users (
  trophy_id   NUMBER       NOT NULL,
  user_id     NUMBER       NOT NULL,
  description VARCHAR2(30) NOT NULL,
  PRIMARY KEY (trophy_id, user_id),
  FOREIGN KEY (trophy_id)
  REFERENCES trophies (id)
  ON DELETE CASCADE,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);

CREATE TABLE sections_users (
  section_id NUMBER NOT NULL,
  user_id    NUMBER NOT NULL,
  PRIMARY KEY (section_id, user_id),
  FOREIGN KEY (section_id)
  REFERENCES sections (id)
  ON DELETE CASCADE,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);

CREATE TABLE tags_topics (
  tag_id   NUMBER NOT NULL,
  topic_id NUMBER NOT NULL,
  PRIMARY KEY (topic_id, tag_id),
  FOREIGN KEY (topic_id)
  REFERENCES topics (id)
  ON DELETE CASCADE,
  FOREIGN KEY (tag_id)
  REFERENCES tags (id)
  ON DELETE CASCADE
);

CREATE TABLE likes (
  message_id NUMBER NOT NULL,
  user_id    NUMBER NOT NULL,
  PRIMARY KEY (message_id, user_id),
  FOREIGN KEY (message_id)
  REFERENCES messages (id)
  ON DELETE CASCADE,
  FOREIGN KEY (user_id)
  REFERENCES users (id)
  ON DELETE CASCADE
);
