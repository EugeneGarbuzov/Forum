from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


# Create your views here.


def login(request):
    if request.method == 'POST':
        login = request.POST['Login']
        password = request.POST['Password']
        user = auth.authenticate(username=login, password=password)
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {
                'error': 1,
            })
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
