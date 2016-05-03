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

