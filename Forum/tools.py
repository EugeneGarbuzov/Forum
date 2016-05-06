from django.contrib.auth.models import User
from django.db import connection


def fetch_to_dict(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


def cursor_calfunc(bla, blabla, tuplebla, cursor):
    return cursor.execute('''SELECT tp.name, tp.description, tp.create_date, u.nickname, u.username, s.name AS section_name
                          FROM tags tg, tags_topics tt, topics tp, sections s, ROLES r, USERS u
                          WHERE u.id = tp.user_id
                          AND s.role_id = r.id
                          AND r.name IN {0}
                          AND s.id = tp.section_id
                          AND tp.id = tt.topic_id
                          AND tt.tag_id = tg.id
                          AND tg.name = %s;'''.format(tuplebla[0]), (tuplebla[1],))


def cursor_callfunc(bla, blabla, tuplebla, cursor):
    # Иди своей дорогой, сталкер
    return cursor.execute('''SELECT s.name, s.description, s.create_date,
                          (SELECT name FROM roles WHERE roles.id = s.role_id)  AS role_name
                          FROM sections s, roles r
                          WHERE s.role_id = r.id
                          AND r.name IN {0};'''.format(tuplebla))


def fetch_to_tuple(cursor):
    return tuple(row[0] for row in cursor.fetchall())


class ForumAuthenticationBackend:
    def authenticate(self, username=None, password=None):

        with connection.cursor() as cursor:
            cursor.execute('''SELECT * FROM users
                              WHERE username = %s AND password = %s;''',
                           (username, password))

            if fetch_to_dict(cursor):
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User(username=username, password=password)
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
