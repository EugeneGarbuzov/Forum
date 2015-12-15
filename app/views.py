from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from Forum.tools import fetch_to_dict, check_roles


# Create your views here.


def login(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {'error': 1})
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute('''insert into users(role_id, rank_id, username, password, email, nickname, full_name, date, status,signature)
                                  select role_id, rank_id, %s, %s, %s, %s, %s, now(), %s, %s from roles, ranks
                                  where role_name = 'newbie' and rank_name = 'rank_1';''',
                               (request.POST['username'], request.POST['password'], request.POST['email'],
                                request.POST['nickname'], request.POST['full_name'],
                                request.POST['status'], request.POST['signature']))
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
        except:
            return render(request, 'register.html', {'error': 1})

    return render(request, "register.html")


def profile(request, username):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''select username, nickname, full_name, date, status, signature, role_name
                          from users, roles
                          where users.role_id = roles.role_id
                          and username = %s;''', username)
            user = fetch_to_dict(cursor)[0]
            return render(request, 'profile.html', user)
    except:
        return HttpResponseRedirect(reverse('index'))


def edit_profile(request):
    username = request.user.username

    if not username:
        return HttpResponseRedirect(reverse('index'))
    try:
        with connection.cursor() as cursor:

            if request.method == 'GET':
                cursor.execute('''select email, nickname, full_name, status, signature
                                  from users
                                  where username = %s;''', username)
                user = fetch_to_dict(cursor)[0]
                return render(request, 'edit_profile.html', user)

            elif request.method == 'POST':
                cursor.execute('''update users set password = %s, email = %s, nickname = %s,
                                  full_name = %s, status = %s, signature = %s
                                  where username = %s;''',
                               (request.POST['password'], request.POST['email'],
                                request.POST['nickname'], request.POST['full_name'],
                                request.POST['status'], request.POST['signature'],
                                username))
                return HttpResponseRedirect(reverse('index'))
    except:
        return render(request, 'edit_profile.html', {'error': 1})


def index(request):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''select nickname, role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            nickname, role = cursor.fetchone()
        else:
            nickname = ''
            role = 'newbie'

        roles = check_roles(role)

        cursor.execute('''select s.name, s.description, s.date,
                          (select role_name from roles where roles.role_id = s.role_id)  as role_name
                          from sections as s, roles as r
                          where s.role_id = r.role_id
                          and r.role_name in %s;''', [tuple(roles)])
        sections = fetch_to_dict(cursor)

        for section in sections:
            cursor.execute('''select username, nickname
                              from users, sections, sections_users
                              where users.user_id = sections_users.user_id
                              and sections_users.section_id = sections.section_id
                              and name = %s;''', section['name'])
            section['moderators'] = fetch_to_dict(cursor)

    context = {'user': {'nickname': nickname, 'username': username, 'is_admin': role == 'admin'},
               'sections': sections}

    return render(request, 'index.html', context)


def add_section(request):
    username = request.user.username

    if username:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''select role_name
                                  from users, roles
                                  where roles.role_id = users.role_id
                                  and username = %s;''', username)
                role = cursor.fetchone()[0]

                if role == 'admin':
                    if request.method == 'GET':
                        return render(request, 'add_section.html')
                    elif request.method == 'POST':
                        cursor.execute('''insert into sections(role_id, name, date, description)
                                          select role_id, %s, now(), %s
                                          from roles where role_name = %s;''',
                                       (request.POST['name'], request.POST['description'], request.POST['role_name']))
        except:
            return render(request, 'add_section.html', {'error': 1})

    return HttpResponseRedirect(reverse('index'))


def remove_section(request, section_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            role = cursor.fetchone()[0]

            if role == 'admin':
                cursor.execute('''delete from sections where name = %s''', section_name)

    return HttpResponseRedirect(reverse('index'))


def section(request, section_name):
    username = request.user.username

    with connection.cursor() as cursor:
        if username:
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
        else:
            user_role = 'newbie'

        cursor.execute('''select role_name
                          from sections, roles
                          where roles.role_id = sections.role_id
                          and name = %s;''', section_name)
        section_role = cursor.fetchone()[0]

        if section_role not in check_roles(user_role):
            return HttpResponseRedirect(reverse('index'))

        cursor.execute('''select username
                          from users, sections, sections_users
                          where users.user_id = sections_users.user_id
                          and sections_users.section_id = sections.section_id
                          and name = %s;''', section_name)
        moderators = (row[0] for row in cursor.fetchall())

        is_moderator = user_role == 'admin' or (user_role == 'moderator' and username in moderators)

        cursor.execute('''select t.name, t.description, t.date, u.nickname, u.username, s.name as section_name
                          from topics as t, users as u, sections as s
                          where u.user_id = t.user_id
                          and t.section_id = s.section_id
                          and s.name = %s;''', section_name)
        topics = fetch_to_dict(cursor)

        for topic in topics:
            cursor.execute('''select tag_name from tags_topics
                              join tags on tags.tag_id = tags_topics.tag_id
                              join topics on topics.topic_id = tags_topics.topic_id
                              where name = %s;''', topic['name'])
            topic['tags'] = (row[0] for row in cursor.fetchall())

    context = {'user': {'is_moderator': is_moderator},
               'section_name': section_name,
               'topics': topics}

    return render(request, 'section.html', context)


def add_topic(request, section_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:

            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            if user_role in ('admin', 'moderator'):

                cursor.execute('''select username
                                  from users, sections, sections_users
                                  where users.user_id = sections_users.user_id
                                  and sections_users.section_id = sections.section_id
                                  and name = %s;''', section_name)
                moderators = (row[0] for row in cursor.fetchall())

                if user_role == 'admin' or username in moderators:
                    if request.method == 'GET':
                        return render(request, 'add_topic.html', {'section_name': section_name})

                    elif request.method == 'POST':
                        try:
                            if not request.POST['name']:
                                raise ValueError('Topic name cannot be empty.')

                            cursor.execute('''select name from topics;''')
                            existing_topics = (row[0] for row in cursor.fetchall())
                            if request.POST['name'] in existing_topics:
                                raise ValueError('Such topic already exists.')

                            cursor.execute('''insert into topics(section_id, user_id, name, date, description)
                                              select section_id, user_id, %s, now(), %s
                                              from sections, users
                                              where name = %s
                                              and username = %s;''',
                                           (request.POST['name'], request.POST['description'], section_name, username))

                            if request.POST['tags'] and not request.POST['tags'].isspace():
                                tags = tuple(set(request.POST['tags'].split()))
                                cursor.execute('''select tag_name from tags;''')
                                existing_tags = (row[0] for row in cursor.fetchall())
                                for tag in tags:
                                    if tag not in existing_tags:
                                        cursor.execute('''insert into tags(tag_name) values (%s);''', tag)
                                    cursor.execute('''insert into tags_topics(tag_id, topic_id)
                                                      select tag_id, topic_id from tags, topics
                                                      where tag_name = %s
                                                      and name = %s;''', (tag, request.POST['name']))

                        except:
                            return render(request, 'add_topic.html', {'section_name': section_name, 'error': 1})

    return HttpResponseRedirect(reverse('section', args=(section_name,)))


def remove_topic(request, section_name, topic_name):
    username = request.user.username

    if username:
        with connection.cursor() as cursor:

            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]

            if user_role in ('admin', 'moderator'):

                cursor.execute('''select username
                                  from users, sections, sections_users
                                  where users.user_id = sections_users.user_id
                                  and sections_users.section_id = sections.section_id
                                  and name = %s;''', section_name)
                moderators = (row[0] for row in cursor.fetchall())

                if user_role == 'admin' or username in moderators:
                    cursor.execute('''delete from topics where name = %s''', topic_name)

    return HttpResponseRedirect(reverse('section', args=(section_name,)))

# todo здесь, возможно, баг при просмотре неавторизованным пользователем
def topic(request, section_name, topic_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''select count(*) from sections
                              where name = %s;''', section_name)
            number_of_sections = cursor.fetchone()[0]
            if not number_of_sections:
                raise ValueError('No such section')

            username = request.user.username
            cursor.execute('''select role_name
                              from users, roles
                              where roles.role_id = users.role_id
                              and username = %s;''', username)
            user_role = cursor.fetchone()[0]
            cursor.execute('''select role_name from sections
                              join roles on roles.role_id = sections.role_id
                              where sections.name = %s;''', section_name)
            section_role = cursor.fetchone()[0]
            if section_role not in check_roles(user_role):
                raise Exception('Current user has no access to current section.')

            cursor.execute('''select * from topics
                              join sections on sections.section_id = topics.section_id
                              where sections.name = %s
                              and topics.name = %s;''', (section_name, topic_name))
            number_of_topics = len(cursor.fetchall())
            if not number_of_topics:
                raise ValueError('No such topic in current section.')

            cursor.execute('''select username, text, m.date, rating from messages as m
                              join users as u on u.user_id = m.user_id
                              join topics as t on t.topic_id = m.topic_id
                              join sections as s on s.section_id = t.section_id
                              where s.name = %s
                              and t.name = %s;''', (section_name, topic_name))
            messages = fetch_to_dict(cursor)

            context = {'section_name': section_name, 'topic_name': topic_name, 'messages': messages}

            return render(request, 'topic.html', context)

    except:
        return HttpResponseRedirect(reverse('index'))
