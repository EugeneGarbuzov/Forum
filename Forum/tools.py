import cx_Oracle
from django.contrib.auth.models import User
from django.db import connection


def fetch_to_dict(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


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
            if fetch_to_dict(cursor.callfunc('get_user_info', cx_Oracle.CURSOR, (username, password))):
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
