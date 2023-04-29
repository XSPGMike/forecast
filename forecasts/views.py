from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from dotenv import load_dotenv
from .models import Forecast, Vote
import os

import requests
import json

load_dotenv()

# Create your views here.
def index(request):
    return render(request, "forecasts/index.html", {"forecasts": Forecast.objects.filter(outcome=None), "year": date.today().year})

def archive(request):
    return render(request, "forecasts/index.html", {"forecasts": Forecast.objects.filter(outcome__isnull=False), "year": date.today().year, "archive": True})

def new(request):
    if(request.method == "GET"):
        return render(request, "forecasts/new.html", {"today": str(date.today())})

    deadline, title, description = request.POST["deadline"], request.POST["title"], request.POST["description"]

    # show the votes only after the forecast has ended
    private = bool(request.POST.get("is_private"))

    if deadline and title:
        try:
            forecast = Forecast.objects.create(
                deadline=deadline,
                title=title,
                description=description,
                created_by=request.user,
                private=private
            )
            url = f'http://localhost:8000/forecasts/{forecast.uuid}' if not os.environ.get("PROD") else f'https://forecast.archiviazzo.ninja/forecasts/{forecast.uuid}'
            send_discord_message(f'New forecast {forecast.title} created by {forecast.created_by.username}! Go to predict here: {url}')
            return HttpResponseRedirect("/forecasts")
        except ValueError:
            return render(request, "forecasts/new.html", {"error_message": "Invalid input."})
    else:
        return render(request, "forecasts/new.html", {"error_message": "Invalid input."})

def detail(request, uuid):
    if request.method == "GET":
        forecast = get_object_or_404(Forecast, uuid=uuid)
        return render(request, "forecasts/detail.html", {"forecast": forecast})
    return HttpResponseRedirect("/forecasts")

def vote(request, uuid):
    if request.method == "POST":
        forecast = get_object_or_404(Forecast, uuid=uuid)
        vote = request.POST["vote"]
        if not vote:
            return render(request, "forecasts/detail.html", {"error_message": "Invalid input."})
        forecast.vote_set.create(vote=vote, user=request.user)
        return HttpResponseRedirect("/forecasts")

    return HttpResponseRedirect("/forecasts")

def end(request, uuid):
    if request.method == "POST":
        forecast = get_object_or_404(Forecast, uuid=uuid, created_by=request.user)
        outcome = request.POST["outcome"]
        if not outcome:
            return render(request, "forecasts/detail.html", {"error_message": "Invalid input."})
        forecast.outcome = outcome
        forecast.save()
        url = f'http://localhost:8000/forecasts/{forecast.uuid}' if not os.environ.get("PROD") else f'https://forecast.archiviazzo.ninja/forecasts/{forecast.uuid}'
        send_discord_message(f'Forecast {forecast.title} (created by {forecast.created_by.username}) has ended with the following outcome: {"It happened!" if forecast.outcome == True else "It did not happen!"}, go check results at {url}')
        return HttpResponseRedirect("/forecasts")

    return HttpResponseRedirect("/forecasts")

def send_discord_message(message):
    if os.environ.get("PROD"):
        data = { "content": message }
        hook = os.environ.get("DISCORD_WEBHOOK")
        try:
            result = requests.post(hook, data=json.dumps(data), headers={"Content-Type": "application/json"})
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
    else:
        print(f'Would have sent {message} to discord webhook')
