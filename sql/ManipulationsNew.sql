START TRANSACTION;

USE forum;

INSERT INTO roles (role_name, description) VALUES
  ('admin', 'полный доступ.'),
('moderator', 'руководит закреплёнными за ним разделами.'),
('regular', 'обычный пользователь.'),
('newbie', 'может читать разделы для обычных пользователей, но писать только в песочнице.');

INSERT INTO ranks (rank_name, bonus_rating) VALUES
  ('rank_1', 1),
('rank_2', 2),
('rank_3', 3),
('rank_4', 4);

INSERT INTO trophies (trophy_name) VALUES
  ('trophy_1'),
('trophy_2'),
('trophy_3'),
('trophy_4'),
('trophy_5');

INSERT INTO tags (tag_name) VALUES
  ('tag_1'),
('tag_2'),
('tag_3'),
('tag_4');

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 date,
 status,
 signature)

  SELECT

    role_id,
    rank_id,

    'user_1',
    'user',
    'user1@example.com',

    'user 1',
    'name surname',
    now(),
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.role_name = 'regular' AND ranks.rank_name = 'rank_1';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 date,
 status,
 signature)

  SELECT

    role_id,
    rank_id,

    'user_2',
    'user',
    'user2@example.com',

    'user 2',
    'name surname',
    now(),
    'status',
    'signature'

  FROM roles, ranks
  WHERE role_name = 'newbie' AND rank_name = 'rank_1';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 date,
 status,
 signature)

  SELECT

    role_id,
    rank_id,

    'admin',
    'admin',
    'admin@example.com',

    'admin',
    'name surname',
    now(),
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.role_name = 'admin' AND ranks.rank_name = 'rank_4';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 date,
 status,
 signature)

  SELECT

    role_id,
    rank_id,

    'moderator_1',
    'moderator',
    'moderator1@example.com',

    'moderator 1',
    'name surname',
    now(),
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.role_name = 'moderator' AND ranks.rank_name = 'rank_2';

INSERT INTO users
(role_id,
 rank_id,

 username,
 password,
 email,

 nickname,
 full_name,
 date,
 status,
 signature)

  SELECT

    role_id,
    rank_id,

    'moderator_2',
    'moderator',
    'moderator2@example.com',

    'moderator 2',
    'name surname',
    now(),
    'status',
    'signature'

  FROM roles, ranks
  WHERE roles.role_name = 'moderator' AND ranks.rank_name = 'rank_3';


INSERT INTO journal (user_id, description, date)
  SELECT
    user_id,
    'action',
    now()
  FROM users
  WHERE username = 'user_1';

INSERT INTO journal (user_id, description, date)
  SELECT
    user_id,
    'action',
    now()
  FROM users
  WHERE username = 'user_2';


INSERT INTO sections (role_id, name, date, description) VALUES
  (3, 'section_1', now(), 'description'),
(4, 'section_2', now(), 'description');


INSERT INTO topics (name, date, description, section_id, user_id)
  SELECT
    'topic_1',
    now(),
    'description',
    sections.section_id,
    users.user_id
  FROM sections, users
  WHERE sections.name = 'section_1' AND users.username = 'user_1';

INSERT INTO topics (name, date, description, section_id, user_id)
  SELECT
    'topic_2',
    now(),
    'description',
    sections.section_id,
    users.user_id
  FROM sections, users
  WHERE sections.name = 'section_2' AND users.username = 'user_2';


INSERT INTO messages (date, text, rating, user_id, topic_id)
  SELECT
    now(),
    'message',
    0,
    users.user_id,
    topics.topic_id
  FROM users, topics
  WHERE users.username = 'user_1' AND topics.name = 'topic_1';

INSERT INTO messages (date, text, rating, user_id, topic_id)
  SELECT
    now(),
    'message',
    0,
    users.user_id,
    topics.topic_id
  FROM users, topics
  WHERE users.username = 'user_2' AND topics.name = 'topic_2';


INSERT INTO trophies_users (trophy_id, user_id, description)
  SELECT
    trophies.trophy_id,
    users.user_id,
    'description'
  FROM trophies, users
  WHERE trophies.trophy_name = 'trophy_1' AND users.username = 'user_1';

INSERT INTO trophies_users (trophy_id, user_id, description)
  SELECT
    trophies.trophy_id,
    users.user_id,
    'description'
  FROM trophies, users
  WHERE trophies.trophy_name = 'trophy_2' AND users.username = 'user_2';


INSERT INTO sections_users (section_id, user_id)
  SELECT
    sections.section_id,
    users.user_id
  FROM sections, users
  WHERE sections.name = 'section_1' AND users.username = 'moderator_1';

INSERT INTO sections_users (section_id, user_id)
  SELECT
    sections.section_id,
    users.user_id
  FROM sections, users
  WHERE sections.name = 'section_2' AND users.username = 'moderator_2';


INSERT INTO tags_topics (tag_id, topic_id)
  SELECT
    tags.tag_id,
    topics.topic_id
  FROM tags, topics
  WHERE tags.tag_name = 'tag_1' AND topics.name = 'topic_1';


INSERT INTO tags_topics (tag_id, topic_id)
  SELECT
    tags.tag_id,
    topics.topic_id
  FROM tags, topics
  WHERE tags.tag_name = 'tag_2' AND topics.name = 'topic_2';

COMMIT;
