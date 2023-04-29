from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from forecasts.models import Forecast

from django.contrib.auth.models import User

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def leaderboard(request):
    year = request.GET.get('year')
    forecast_count = Forecast.objects.filter(outcome__isnull=False, deadline__year=year, hidden_to__isnull=True).count()
    if forecast_count == 0:
        return HttpResponseRedirect('/')

    users = User.objects.values('username')
    for user in users:
        user['raw_score'] = 0
        user['score'] = 0
        user['count'] = 0

    other_years = Forecast.objects.values('deadline__year').distinct().exclude(deadline__year=year).filter(outcome__isnull=False).values_list('deadline__year', flat=True)

    for forecast in Forecast.objects.filter(outcome__isnull=False, deadline__year=year, hidden_to__isnull=True):
        for user, score in forecast.scores():
            for u in users:
                if u['username'] == user:
                    u['raw_score'] += score
                    u['count'] += 1

    for user in users:
        if user['raw_score'] == 0:
            #worst brier score
            user['raw_score'], user['score'] = 1.0, 1.0
        else:
            weight = 1 - (user['count'] / forecast_count)
            user['raw_score'] = round(user['raw_score'] / user['count'], 4)
            user['score'] = round(((user['raw_score'] / forecast_count) * weight)*10, 4)

    users = sorted(users, key=lambda k: k['score'])

    return render(request, 'users/leaderboard.html', {'users': enumerate(users) , 'years': other_years})

def profile(request):
    if request.user is None:
        return HttpResponseRedirect('/login')

    if request.method == "POST":
        password, confirm = request.POST.get('password'), request.POST.get('confirm')
        if password != confirm:
            return render(request, 'users/profile.html', {'error': 'Passwords do not match'})
        if len(password) < 8 or len(password) > 32:
            return render(request, 'users/profile.html', {'error': 'Password must be between 8 and 32 characters'})
        try: 
            request.user.set_password(password)
            request.user.save()
            return HttpResponseRedirect('/forecasts')
        except Exception as e:
            return render(request, 'users/profile.html', {'error': 'Invalid password'})

    return render(request, 'users/profile.html')
