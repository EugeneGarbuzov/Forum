INSERT INTO roles (name, description) VALUES
  ('admin', 'полный доступ.');
INSERT INTO roles (name, description) VALUES
  ('moderator', 'руководит закреплёнными за ним разделами.');
INSERT INTO roles (name, description) VALUES
  ('regular', 'обычный пользователь.');
INSERT INTO roles (name, description) VALUES
  ('newbie', 'может читать разделы для обычных пользователей, но писать только в песочнице.');

INSERT INTO ranks (name, bonus_rating) VALUES
  ('rank_1', 1);
INSERT INTO ranks (name, bonus_rating) VALUES
  ('rank_2', 2);
INSERT INTO ranks (name, bonus_rating) VALUES
  ('rank_3', 3);
INSERT INTO ranks (name, bonus_rating) VALUES
  ('rank_4', 4);

INSERT INTO trophies (name) VALUES
  ('trophy_1');
INSERT INTO trophies (name) VALUES
  ('trophy_2');
INSERT INTO trophies (name) VALUES
  ('trophy_3');
INSERT INTO trophies (name) VALUES
  ('trophy_4');
INSERT INTO trophies (name) VALUES
  ('trophy_5');

INSERT INTO tags (name) VALUES
  ('tag_1');
INSERT INTO tags (name) VALUES
  ('tag_2');
INSERT INTO tags (name) VALUES
  ('tag_3');
INSERT INTO tags (name) VALUES
  ('tag_4');

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 join_date,
 status,
 signature)

  SELECT

    roles.id,
    ranks.id,

    'user_1',
    'user',
    'user1@example.com',

    'user 1',
    'name surname',
    CURRENT_DATE,
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.name = 'regular' AND ranks.name = 'rank_1';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 join_date,
 status,
 signature)

  SELECT

    roles.id,
    ranks.id,

    'user_2',
    'user',
    'user2@example.com',

    'user 2',
    'name surname',
    CURRENT_DATE,
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.name = 'newbie' AND ranks.name = 'rank_1';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 join_date,
 status,
 signature)

  SELECT

    roles.id,
    ranks.id,

    'admin',
    'admin',
    'admin@example.com',

    'admin',
    'name surname',
    CURRENT_DATE,
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.name = 'admin' AND ranks.name = 'rank_4';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 join_date,
 status,
 signature)

  SELECT

    roles.id,
    ranks.id,

    'moderator_1',
    'moderator',
    'moderator1@example.com',

    'moderator 1',
    'name surname',
    CURRENT_DATE,
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.name = 'moderator' AND ranks.name = 'rank_2';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 join_date,
 status,
 signature)

  SELECT

    roles.id,
    ranks.id,

    'moderator_2',
    'moderator',
    'moderator2@example.com',

    'moderator 2',
    'name surname',
    CURRENT_DATE,
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.name = 'moderator' AND ranks.name = 'rank_3';


INSERT INTO journal (user_id, description, entry_date)
  SELECT
    id,
    'action',
    CURRENT_DATE
  FROM users
  WHERE username = 'user_1';

INSERT INTO journal (user_id, description, entry_date)
  SELECT
    id,
    'action',
    CURRENT_DATE
  FROM users
  WHERE username = 'user_2';


INSERT INTO sections (role_id, name, create_date, description) VALUES
  (3, 'section_1', CURRENT_DATE, 'description');
INSERT INTO sections (role_id, name, create_date, description) VALUES
  (4, 'section_2', CURRENT_DATE, 'description');


INSERT INTO topics (name, create_date, description, section_id, user_id)
  SELECT
    'topic_1',
    CURRENT_DATE,
    'description',
    sections.id,
    users.id
  FROM sections, users
  WHERE sections.name = 'section_1' AND users.username = 'user_1';

INSERT INTO topics (name, create_date, description, section_id, user_id)
  SELECT
    'topic_2',
    CURRENT_DATE,
    'description',
    sections.id,
    users.id
  FROM sections, users
  WHERE sections.name = 'section_2' AND users.username = 'user_2';


INSERT INTO messages (create_date, text, rating, user_id, topic_id)
  SELECT
    CURRENT_DATE,
    'message',
    0,
    users.id,
    topics.id
  FROM users, topics
  WHERE users.username = 'user_1' AND topics.name = 'topic_1';

INSERT INTO messages (create_date, text, rating, user_id, topic_id)
  SELECT
    CURRENT_DATE,
    'message',
    0,
    users.id,
    topics.id
  FROM users, topics
  WHERE users.username = 'user_2' AND topics.name = 'topic_2';


INSERT INTO trophies_users (trophy_id, user_id, description)
  SELECT
    trophies.id,
    users.id,
    'description'
  FROM trophies, users
  WHERE trophies.name = 'trophy_1' AND users.username = 'user_1';

INSERT INTO trophies_users (trophy_id, user_id, description)
  SELECT
    trophies.id,
    users.id,
    'description'
  FROM trophies, users
  WHERE trophies.name = 'trophy_2' AND users.username = 'user_2';


INSERT INTO sections_users (section_id, user_id)
  SELECT
    sections.id,
    users.id
  FROM sections, users
  WHERE sections.name = 'section_1' AND users.username = 'moderator_1';

INSERT INTO sections_users (section_id, user_id)
  SELECT
    sections.id,
    users.id
  FROM sections, users
  WHERE sections.name = 'section_2' AND users.username = 'moderator_2';


INSERT INTO tags_topics (tag_id, topic_id)
  SELECT
    tags.id,
    topics.id
  FROM tags, topics
  WHERE tags.name = 'tag_1' AND topics.name = 'topic_1';


INSERT INTO tags_topics (tag_id, topic_id)
  SELECT
    tags.id,
    topics.id
  FROM tags, topics
  WHERE tags.name = 'tag_2' AND topics.name = 'topic_2';