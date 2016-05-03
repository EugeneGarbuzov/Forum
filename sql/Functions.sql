CREATE OR REPLACE PROCEDURE log(user_name VARCHAR2, message VARCHAR2)
IS
  BEGIN
    INSERT INTO journal(user_id, description, entry_date)
                          SELECT id, message, CURRENT_DATE FROM USERS
                          WHERE username = user_name;
  END log;