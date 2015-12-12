from django.db import connection


def fetch_to_dict(cursor):
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


class ForumAuthenticationBackend:
    def authenticate(self, username=None, password=None):

        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM users
                          WHERE login = %s
                          AND password = %s;''', [username, password])

        lol = fetch_to_dict(cursor)
        if lol:
            print(lol)

            # login_valid = (settings.ADMIN_LOGIN == username)
            # pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
            # if login_valid and pwd_valid:
            #     try:
            #         user = User.objects.get(username=username)
            #     except User.DoesNotExist:
            #         # Create a new user. Note that we can set password
            #         # to anything, because it won't be checked; the password
            #         # from settings.py will.
            #         user = User(username=username, password='get from settings.py')
            #         user.is_staff = True
            #         user.is_superuser = True
            #         user.save()
            #     return user
            # return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
