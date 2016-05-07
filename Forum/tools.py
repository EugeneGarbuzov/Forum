import cx_Oracle
from django.contrib.auth.models import User
from django.db import connection


def fetch_to_dict(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


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
