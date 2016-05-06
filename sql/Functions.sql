CREATE OR REPLACE PROCEDURE log_add(username_ VARCHAR2, message VARCHAR2)
IS
  BEGIN
    INSERT INTO journal (user_id, description, entry_date)
      SELECT
        id,
        message,
        CURRENT_DATE
      FROM USERS
      WHERE username = username_;
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


CREATE OR REPLACE FUNCTION user_info(username_ VARCHAR2)
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
                          AND username = username_;
    RETURN result;
  END user_info;
/


CREATE OR REPLACE FUNCTION user_trophies(username_ VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      name,
                      description
                    FROM trophies, trophies_users, users
                    WHERE trophies.id = trophies_users.trophy_id
                          AND trophies_users.user_id = users.id
                          AND username = username_;
    RETURN result;
  END user_trophies;
/


CREATE OR REPLACE FUNCTION user_moderated_sections(username_ VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT sections.name
                    FROM users, sections_users, sections
                    WHERE sections.id = sections_users.section_id
                          AND sections_users.user_id = users.id
                          AND username = username_;
    RETURN result;
  END user_moderated_sections;
/


CREATE OR REPLACE FUNCTION private_user_info(username_ VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      email,
                      nickname,
                      full_name,
                      status,
                      signature
                    FROM users
                    WHERE username = username_;
    RETURN result;
  END private_user_info;
/


CREATE OR REPLACE PROCEDURE update_private_user_info(username_ VARCHAR2, password_ VARCHAR2, email_ VARCHAR2,
                                                     nickname_ VARCHAR2, full_name_ VARCHAR2,
                                                     status_   VARCHAR2, signature_ VARCHAR2)
IS
  BEGIN
    UPDATE users
    SET password = password_, email = email_, nickname = nickname_,
      full_name  = full_name_, status = status_, signature = signature_
    WHERE username = username_;

    log_add(username_, 'edited profile');
  END update_private_user_info;
/


CREATE OR REPLACE FUNCTION user_role(username_ VARCHAR2)
  RETURN VARCHAR2
IS
  role VARCHAR2(30);
  BEGIN
    SELECT name
    INTO role
    FROM users, roles
    WHERE roles.id = users.role_id AND username = username_;
    RETURN role;
  END user_role;
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


CREATE OR REPLACE PROCEDURE add_section(username_ VARCHAR2, name_ VARCHAR2, description_ VARCHAR2, role_ VARCHAR2)
IS
  role VARCHAR2(30);
  BEGIN
    role := user_role(username_);

    IF role = 'admin'
    THEN

      INSERT INTO sections (role_id, name, create_date, description)
        SELECT
          id,
          name_,
          CURRENT_DATE,
          description_
        FROM ROLES
        WHERE NAME = role_;
      log_add(username_, 'added section ' || name_);
    END IF;

  END add_section;
/


CREATE OR REPLACE PROCEDURE remove_section(username_ VARCHAR2, name_ VARCHAR2)
IS
  role VARCHAR2(30);
  BEGIN
    role := user_role(username_);

    IF role = 'admin'
    THEN
      DELETE FROM sections
      WHERE name = name_;
      log_add(username_, 'removed section' || name_);
    END IF;

  END remove_section;
/


CREATE OR REPLACE FUNCTION section_role(section_name VARCHAR2)
  RETURN VARCHAR2
IS
  role VARCHAR2(30);
  BEGIN
    SELECT roles.name
    INTO role
    FROM sections, roles
    WHERE roles.id = sections.role_id
          AND sections.name = section_name;
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


CREATE OR REPLACE PROCEDURE add_topic(username_ VARCHAR2, section_name VARCHAR2, name_ VARCHAR2, description_ VARCHAR2)
IS
  BEGIN
    INSERT INTO topics (section_id, user_id, name, create_date, description)
      SELECT
        sections.id,
        users.id,
        name_,
        CURRENT_DATE,
        description_
      FROM sections, users
      WHERE NAME = section_name
            AND username = username_;

    log_add(username_, 'added topic ' || name_);
  END add_topic;
/


CREATE OR REPLACE FUNCTION is_moderator(username_ VARCHAR2, section_name VARCHAR2)
  RETURN NUMBER
IS
  role VARCHAR2(30);
  BEGIN
    role := user_role(username_);

    IF role = 'admin'
    THEN
      RETURN 1;
    END IF;

    IF role = 'moderator'
    THEN
      FOR moderator IN (SELECT username
                        FROM users, sections, sections_users
                        WHERE users.id = sections_users.user_id
                              AND sections_users.section_id = sections.id
                              AND name = section_name)
      LOOP
        IF moderator.username = username_
        THEN
          RETURN 1;
        END IF;
      END LOOP;
    END IF;

    RETURN 0;
  END is_moderator;
/


CREATE OR REPLACE PROCEDURE remove_topic(username_ VARCHAR2, topic_name VARCHAR2)
IS
  role VARCHAR2(30);
  BEGIN
    role := user_role(username_);

    IF role = 'admin'
    THEN
      DELETE FROM topics
      WHERE name = topic_name;
      log_add(username_, 'removed topic ' || topic_name);
      RETURN;
    END IF;

    IF role = 'moderator'
    THEN
      FOR moderator IN (SELECT username
                        FROM users, sections_users, topics, messages
                        WHERE users.id = sections_users.user_id
                              AND sections_users.section_id = topics.section_id
                              AND topics.name = topic_name)
      LOOP
        IF moderator.username = username_
        THEN
          DELETE FROM topics
          WHERE name = topic_name;
          log_add(username_, 'removed topic ' || topic_name);
          RETURN;
        END IF;
      END LOOP;
    END IF;

  END remove_topic;
/


CREATE OR REPLACE FUNCTION topic_exists(topic_name VARCHAR2)
  RETURN NUMBER
IS
  result NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO result
    FROM topics
    WHERE topics.name = topic_name;
    RETURN result;
  END topic_exists;
/


CREATE OR REPLACE PROCEDURE add_tag(topic_name VARCHAR2, tag_ VARCHAR2)
IS
  tag_exists NUMBER := 0;
  BEGIN
    BEGIN
      SELECT 1
      INTO tag_exists
      FROM dual
      WHERE tag_ IN (SELECT name
                     FROM tags);
      EXCEPTION
      WHEN NO_DATA_FOUND THEN
      INSERT INTO tags (name) VALUES (tag_);
    END;
    INSERT INTO tags_topics (tag_id, topic_id)
      SELECT
        tags.id,
        topics.id
      FROM tags, topics
      WHERE tags.name = tag_
            AND topics.name = topic_name;
  END add_tag;
/


CREATE OR REPLACE FUNCTION get_messages(topic_name VARCHAR2)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      messages.id,
                      username,
                      nickname,
                      text,
                      messages.create_date,
                      rating
                    FROM messages, users, topics
                    WHERE users.id = messages.user_id
                          AND messages.topic_id = topics.id
                          AND topics.name = topic_name;
    RETURN result;
  END get_messages;
/


CREATE OR REPLACE PROCEDURE add_message(username_ VARCHAR2, topic_name VARCHAR2, text VARCHAR2)
IS
  BEGIN
    INSERT INTO messages (create_date, text, rating, user_id, topic_id)
      SELECT
        CURRENT_DATE,
        text,
        0,
        users.id,
        topics.id
      FROM users, topics
      WHERE username = username_
            AND name = topic_name;

    log_add(username_, 'added a message');
  END add_message;
/


CREATE OR REPLACE PROCEDURE add_like(username_ VARCHAR2, message_id_ NUMBER)
IS
  already_liked NUMBER;
  author_name   VARCHAR2(30);
  rating_to_add NUMBER;

  BEGIN
    SELECT COUNT(*)
    INTO already_liked
    FROM likes
      JOIN users ON users.id = user_id
    WHERE message_id = message_id_
          AND username = username_;

    IF already_liked > 0
    THEN
      RETURN;
    END IF;
    SELECT username
    INTO author_name
    FROM messages
      JOIN users ON users.id = messages.user_id
    WHERE messages.id = message_id_;

    IF username_ = author_name
    THEN
      RETURN;
    END IF;

    SELECT bonus_rating
    INTO rating_to_add
    FROM users, ranks
    WHERE ranks.id = users.rank_id
          AND username = username_;

    UPDATE messages
    SET rating = messages.rating + rating_to_add
    WHERE id = message_id_;

    INSERT INTO likes (message_id, user_id)
      SELECT
        message_id_,
        id
      FROM users
      WHERE username = username_;

  END add_like;
/


CREATE OR REPLACE PROCEDURE remove_message(username_ VARCHAR2, message_id NUMBER)
IS
  role            VARCHAR2(30);
  message_creator VARCHAR2(30);
  topic_id        NUMBER;

  BEGIN
    role := user_role(username_);

    SELECT username
    INTO message_creator
    FROM messages, users
    WHERE users.id = messages.user_id AND messages.id = message_id;

    IF username_ = message_creator OR role = 'admin'
    THEN
      DELETE FROM messages
      WHERE id = message_id;
      log_add(username_, 'removed message id: ' || message_id);
      RETURN;
    END IF;

    IF role = 'moderator'
    THEN
      FOR moderator IN (SELECT username
                        FROM users, sections_users, topics, messages
                        WHERE users.id = sections_users.user_id
                              AND sections_users.section_id = topics.section_id
                              AND topics.id = messages.topic_id
                              AND messages.id = message_id)
      LOOP
        IF moderator.username = username_
        THEN
          DELETE FROM messages
          WHERE id = message_id;
          log_add(username_, 'removed message id: ' || message_id);
          RETURN;
        END IF;
      END LOOP;
    END IF;

  END remove_message;
/


CREATE OR REPLACE FUNCTION get_message(message_id NUMBER)
  RETURN SYS_REFCURSOR AS result SYS_REFCURSOR;
  BEGIN
    OPEN result FOR SELECT
                      messages.id,
                      username,
                      nickname,
                      text,
                      messages.create_date,
                      rating
                    FROM messages, users
                    WHERE users.id = messages.user_id
                          AND messages.id = message_id;
    RETURN result;
  END get_message;
/


CREATE OR REPLACE PROCEDURE edit_message(username_ VARCHAR2, message_id NUMBER, text_ VARCHAR2)
IS
  role            VARCHAR2(30);
  message_creator VARCHAR2(30);
  topic_id        NUMBER;

  BEGIN
    role := user_role(username_);

    SELECT username
    INTO message_creator
    FROM messages, users
    WHERE users.id = messages.user_id AND messages.id = message_id;

    IF username_ = message_creator OR role = 'admin'
    THEN
      UPDATE messages
      SET text = text_
      WHERE id = message_id;
      log_add(username_, 'edited message id ' || message_id);
      RETURN;
    END IF;

    IF role = 'moderator'
    THEN
      FOR moderator IN (SELECT username
                        FROM users, sections_users, topics, messages
                        WHERE users.id = sections_users.user_id
                              AND sections_users.section_id = topics.section_id
                              AND topics.id = messages.topic_id
                              AND messages.id = message_id)
      LOOP
        IF moderator.username = username_
        THEN
          UPDATE messages
          SET text = text_
          WHERE id = message_id;
          log_add(username_, 'edited message id ' || message_id);
          RETURN;
        END IF;
      END LOOP;
    END IF;

  END edit_message;
/