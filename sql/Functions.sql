CREATE OR REPLACE PROCEDURE log_add(user_name VARCHAR2, message VARCHAR2)
IS
  BEGIN
    INSERT INTO journal (user_id, description, entry_date)
      SELECT
        id,
        message,
        CURRENT_DATE
      FROM USERS
      WHERE username = user_name;
  END log_add;
  /


CREATE OR REPLACE PROCEDURE register(username  VARCHAR2, password VARCHAR2, email VARCHAR2, nickname VARCHAR2,
                                     full_name VARCHAR2, status VARCHAR2, signature VARCHAR2)
IS
  BEGIN
    INSERT INTO users (role_id, rank_id, username, password, email, nickname, full_name, join_date, status, signature)
      SELECT
        roles.id,
        ranks.id,
        username,
        password,
        email,
        nickname,
        full_name,
        CURRENT_DATE,
        status,
        signature
      FROM ROLES, ranks
      WHERE ROLES.name = 'newbie' AND ranks.name = 'rank_1';

    log_add(username, 'registered');
  END register;
  /


-- CREATE OR REPLACE TRIGGER register_log
-- AFTER INSERT ON users FOR EACH ROW
--   BEGIN
--     log_add(:new.username, 'registered');
--   END;
--
-- DROP TRIGGER register_log;


CREATE OR REPLACE FUNCTION check_roles(role VARCHAR2, access_mode VARCHAR2 DEFAULT 'read')
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    IF role = 'admin'
    THEN
      OPEN result FOR SELECT name
                      FROM roles;
      RETURN result;
    END IF;

    IF role = 'moderator'
    THEN
      OPEN result FOR SELECT name
                      FROM roles
                      WHERE name != 'admin';
      RETURN result;
    END IF;

    IF role = 'regular'
    THEN
      OPEN result FOR SELECT name
                      FROM roles
                      WHERE name NOT IN ('admin', 'moderator');
      RETURN result;
    END IF;

    IF role = 'newbie'
    THEN
      IF access_mode = 'read'
      THEN
        OPEN result FOR SELECT name
                        FROM roles
                        WHERE name NOT IN ('admin', 'moderator');
        RETURN result;
      ELSIF access_mode = 'write'
        THEN
          OPEN result FOR SELECT name
                          FROM roles
                          WHERE name = 'newbie';
          RETURN result;
      END IF;
    END IF;

  END check_roles;
  /


CREATE OR REPLACE FUNCTION user_info(user_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      username,
                      nickname,
                      full_name,
                      join_date,
                      status,
                      signature,
                      roles.name AS ROLE_NAME,
                      RANKS.name AS RANK_NAME,
                      bonus_rating
                    FROM USERS, ROLES, RANKS
                    WHERE USERS.role_id = ROLES.id
                          AND ranks.id = USERS.rank_id
                          AND username = user_name;
    RETURN result;
  END user_info;
  /


CREATE OR REPLACE FUNCTION user_trophies(user_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      name,
                      description
                    FROM trophies, trophies_users, users
                    WHERE trophies.id = trophies_users.trophy_id
                          AND trophies_users.user_id = users.id
                          AND username = user_name;
    RETURN result;
  END user_trophies;
  /


CREATE OR REPLACE FUNCTION user_moderated_sections(user_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT sections.name
                    FROM users, sections_users, sections
                    WHERE sections.id = sections_users.section_id
                          AND sections_users.user_id = users.id
                          AND username = user_name;
    RETURN result;
  END user_moderated_sections;
  /


CREATE OR REPLACE FUNCTION private_user_info(user_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      email,
                      nickname,
                      full_name,
                      status,
                      signature
                    FROM users
                    WHERE username = user_name;
    RETURN result;
  END private_user_info;
  /


CREATE OR REPLACE PROCEDURE update_private_user_info(user_name    VARCHAR2, password_new VARCHAR2, email_new VARCHAR2,
                                                     nickname_new VARCHAR2, full_name_new VARCHAR2,
                                                     status_new   VARCHAR2, signature_new VARCHAR2)
IS
  BEGIN
    UPDATE users
    SET password = password_new, email = email_new, nickname = nickname_new,
      full_name  = full_name_new, status = status_new, signature = signature_new
    WHERE username = user_name;

    log_add(user_name, 'edited profile');
  END update_private_user_info;
  /


CREATE OR REPLACE FUNCTION user_role_nickname(user_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      nickname,
                      name
                    FROM users, roles
                    WHERE roles.id = users.role_id AND username = user_name;
    RETURN result;
  END user_role_nickname;
  /


CREATE OR REPLACE FUNCTION get_section_moderators(section_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      username,
                      nickname
                    FROM users, sections, sections_users
                    WHERE users.id = sections_users.user_id
                          AND sections_users.section_id = sections.id
                          AND name = section_name;
    RETURN result;
  END get_section_moderators;
  /


CREATE OR REPLACE PROCEDURE add_section(user_name VARCHAR2, name_ VARCHAR2, description_ VARCHAR2, role VARCHAR2)
IS
  BEGIN
    INSERT INTO sections (role_id, name, create_date, description)
      SELECT
        id,
        name_,
        CURRENT_DATE,
        description_
      FROM ROLES
      WHERE NAME = role;

    log_add(user_name, 'added section ' || name_);
  END add_section;
  /


CREATE OR REPLACE PROCEDURE remove_section(user_name VARCHAR2, name_ VARCHAR2)
IS
  role VARCHAR2(30);
  BEGIN
    SELECT name
    INTO role
    FROM users, roles
    WHERE roles.id = users.role_id AND username = user_name;

    IF role = 'admin'
    THEN
      DELETE FROM sections
      WHERE name = name_;
      log_add(user_name, 'removed section' || name_);
    END IF;

  END remove_section;
  /


CREATE OR REPLACE FUNCTION section_role(name_ VARCHAR2)
  RETURN VARCHAR2
IS
  role VARCHAR2(30);
  BEGIN
    SELECT roles.name
    INTO role
    FROM sections, roles
    WHERE roles.id = sections.role_id
          AND sections.name = name_;
    RETURN role;
  END section_role;
  /


CREATE OR REPLACE FUNCTION get_topics(section_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      t.name,
                      t.description,
                      t.create_date,
                      u.nickname,
                      u.username,
                      s.name AS section_name
                    FROM topics t, users u, sections s
                    WHERE u.id = t.user_id
                          AND t.section_id = s.id
                          AND s.name = section_name;
    RETURN result;
  END get_topics;
  /


CREATE OR REPLACE FUNCTION get_topic_tags(topic_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT tags.name
                    FROM tags_topics
                      JOIN tags ON tags.id = tags_topics.tag_id
                      JOIN topics ON topics.id = tags_topics.topic_id
                    WHERE topics.name = topic_name;
    RETURN result;
  END get_topic_tags;
  /

CREATE OR REPLACE PROCEDURE add_topic
  (name_ VARCHAR2, description_ VARCHAR2, section_name VARCHAR2, username_ VARCHAR2)
IS
  BEGIN
    INSERT INTO topics(section_id, user_id, name, create_date, description)
      SELECT sections.id, users.id, name_, CURRENT_DATE, description_
      FROM sections, users
      WHERE NAME = section_name
      AND username = username_;

    log_add(username_, ' added topic ' || name_);
  END add_topic;
  /

CREATE OR REPLACE PROCEDURE remove_topic(topic_name VARCHAR2, username VARCHAR2)
IS
  BEGIN
    DELETE FROM topics WHERE name = topic_name;
    log_add(username || ' removed topic ' || topic_name);
  END remove_topic;
  /
