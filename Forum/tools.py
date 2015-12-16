from django.contrib.auth.models import User
from django.db import connection


def fetch_to_dict(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


def check_roles(role, mode='read'):
    if role == 'admin':
        return 'admin', 'moderator', 'regular', 'newbie'

    if role == 'moderator':
        return 'moderator', 'regular', 'newbie'

    if role == 'regular':
        return 'regular', 'newbie'

    if role == 'newbie':
        if mode == 'read':
            return 'regular', 'newbie'
        elif mode == 'write':
            return 'newbie',


def log(username, message):
    with connection.cursor() as cursor:
        cursor.execute('''insert into journal(user_id, description, date)
                          select user_id, %s, now() from users
                          where username = %s;''',
                       (message, username))


class ForumAuthenticationBackend:
    def authenticate(self, username=None, password=None):

        with connection.cursor() as cursor:
            cursor.execute('''select * from users
                              where username = %s and password = %s;''',
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
