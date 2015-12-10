from django.db import connection
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render


def index(request):
    cursor = connection.cursor()
    cursor.execute("SELECT Name, Description, sections.Date, Login FROM sections\
                        JOIN users ON sections.User_ID = users.User_ID;")
    context = {'cursor': cursor}
    return render(request, "index.html", context)


def section(request, section_name):
    cursor = connection.cursor()
    cursor.execute("SELECT topics.Name, topics.Description,  topics.Date, Login, sections.Date FROM topics\
                        JOIN users ON users.User_ID = topics.User_ID\
                        JOIN sections ON sections.Section_ID = topics.Section_ID\
                        WHERE sections.Name = %s;", [section_name])
    context = {'cursor': cursor}
    return render(request, "section.html", context)


def topic(request, section_name, topic_name):
    # todo implement
    return HttpResponse("Not implemented yet.")
