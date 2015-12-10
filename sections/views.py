from django.db import connection
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render


def index(request):
    cursor = connection.cursor()
    cursor.execute("SELECT Login, Name, sections.Date, Description FROM sections\
                        JOIN users ON sections.User_ID = users.User_ID")
    context = {'cursor': cursor}
    return render(request, "index.html", context)


def section(request, section_name):
    return HttpResponse('Not implemented yet.')
