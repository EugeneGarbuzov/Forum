CREATE OR REPLACE PROCEDURE log_add(username VARCHAR2, message VARCHAR2)
IS
  BEGIN
    INSERT INTO journal (user_id, description, entry_date)
      SELECT
        id,
        message,
        CURRENT_DATE
      FROM USERS
      WHERE username = username;
  END log_add;

CREATE OR REPLACE PROCEDURE register(username  VARCHAR2, password VARCHAR2, email VARCHAR2, nickname VARCHAR2,
                                     full_name VARCHAR2, status VARCHAR2, signature VARCHAR2)
IS
  BEGIN
    INSERT INTO users(role_id, rank_id, username, password, email, nickname, full_name, join_date, status, signature)
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
