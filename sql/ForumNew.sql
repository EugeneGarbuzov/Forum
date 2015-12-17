DROP DATABASE IF EXISTS forum;
CREATE DATABASE forum;

-- create user 'admin'@'localhost' identified by '1234';
-- grant all privileges on forum.* to 'admin'@'localhost';
-- flush privileges;
-- 
-- show grants for 'admin'@'localhost';

USE forum;

CREATE TABLE roles (
    role_id     SERIAL,
    role_name   VARCHAR(30) NOT NULL,
    description TEXT        NOT NULL,
    PRIMARY KEY (role_id),
    UNIQUE (role_name)
);

CREATE TABLE ranks (
    rank_id      SERIAL,
    rank_name    VARCHAR(30)      NOT NULL,
    bonus_rating INTEGER UNSIGNED NOT NULL,
    PRIMARY KEY (rank_id),
    UNIQUE (rank_name)
);

CREATE TABLE trophies (
    trophy_id    SERIAL,
    trophy_name  VARCHAR(30) NOT NULL,
    trophy_image LONGBLOB    NULL,
    PRIMARY KEY (trophy_id),
    UNIQUE (trophy_name)
);

CREATE TABLE tags (
    tag_id   SERIAL,
    tag_name VARCHAR(30) NOT NULL,
    PRIMARY KEY (tag_id),
    UNIQUE (tag_name)
);

CREATE TABLE users (
    user_id    SERIAL,
    role_id    BIGINT UNSIGNED NOT NULL,
    rank_id    BIGINT UNSIGNED NOT NULL,
    username   VARCHAR(30)     NOT NULL,
    password   VARCHAR(30)     NOT NULL,
    email      VARCHAR(30)     NOT NULL,
    user_image LONGBLOB        NULL,
    nickname   VARCHAR(30)     NOT NULL,
    full_name  VARCHAR(30)     NOT NULL,
    date       DATETIME        NOT NULL,
    status     VARCHAR(30)     NOT NULL,
    signature  VARCHAR(50)     NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (role_id)
    REFERENCES roles (role_id),
    FOREIGN KEY (rank_id)
    REFERENCES ranks (rank_id),
    UNIQUE (username, email)
);

CREATE TABLE journal (
    entry_id    SERIAL,
    user_id     BIGINT UNSIGNED NOT NULL,
    description TEXT            NOT NULL,
    date        DATETIME        NOT NULL,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE TABLE sections (
    section_id  SERIAL,
    role_id     BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(30)     NOT NULL,
    date        DATETIME        NOT NULL,
    description VARCHAR(30)     NOT NULL,
    PRIMARY KEY (section_id),
    FOREIGN KEY (role_id)
    REFERENCES roles (role_id),
    UNIQUE (name)
);

CREATE TABLE topics (
    topic_id    SERIAL,
    user_id     BIGINT UNSIGNED NOT NULL,
    section_id  BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(30)     NOT NULL,
    date        DATETIME        NOT NULL,
    description VARCHAR(30)     NOT NULL,
    PRIMARY KEY (topic_id),
    FOREIGN KEY (section_id)
    REFERENCES sections (section_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE,
    UNIQUE (name)
);

CREATE TABLE messages (
    message_id SERIAL,
    user_id    BIGINT UNSIGNED  NOT NULL,
    topic_id   BIGINT UNSIGNED  NOT NULL,
    date       DATETIME         NOT NULL,
    text       TEXT             NOT NULL,
    rating     INTEGER UNSIGNED NOT NULL,
    PRIMARY KEY (message_id),
    FOREIGN KEY (topic_id)
    REFERENCES topics (topic_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE TABLE trophies_users (
    trophy_id   BIGINT UNSIGNED NOT NULL,
    user_id     BIGINT UNSIGNED NOT NULL,
    description VARCHAR(30)     NOT NULL,
    PRIMARY KEY (trophy_id, user_id),
    FOREIGN KEY (trophy_id)
    REFERENCES trophies (trophy_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE TABLE sections_users (
    section_id BIGINT UNSIGNED NOT NULL,
    user_id    BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (section_id, user_id),
    FOREIGN KEY (section_id)
    REFERENCES sections (section_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE TABLE tags_topics (
    tag_id   BIGINT UNSIGNED NOT NULL,
    topic_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (topic_id, tag_id),
    FOREIGN KEY (topic_id)
    REFERENCES topics (topic_id)
        ON DELETE CASCADE,
    FOREIGN KEY (tag_id)
    REFERENCES tags (tag_id)
        ON DELETE CASCADE
);

CREATE TABLE likes (
    message_id BIGINT UNSIGNED NOT NULL,
    user_id    BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (message_id, user_id),
    FOREIGN KEY (message_id)
    REFERENCES messages (message_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
        ON DELETE CASCADE
);

-- create table roles_sections
-- (
-- 	role_id              bigint unsigned not null,
-- 	section_id           bigint unsigned not null,
--     
-- 	primary key (role_id,section_id),
-- 	foreign key (role_id) references roles (role_id) on delete cascade,
-- 	foreign key (section_id) references sections (section_id) on delete cascade
-- );