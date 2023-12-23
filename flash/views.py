from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from sesame.utils import get_token
import json

from .models import Flash

# Create your views here.
class FlashCreateView(CreateView):
    model = Flash
    fields = ["title"]
    success_url = "/flash"
    template_name = "flash/new.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ArchiveListView(ListView):
    model = Flash
    template_name = "flash/archive.html"
    context_object_name = "flashes"
    paginate_by = 10

@login_required(login_url="/users/login")
def index(request):
    flash = Flash.objects.filter(active=True).first()
    if flash:
        return redirect(f"/flash/{flash.uuid}")
    return FlashCreateView.as_view()(request)

@login_required(login_url="/users/login")
def flash(request, uuid):
    flash = Flash.objects.filter(uuid=uuid).first()

    if not flash:
        return redirect("/")
    if flash.active:
        token = get_token(request.user)
        return render(request, "flash/flash.html", { "flash": flash , "token": token })

    results = None
    if flash.outcome == False:
        results = dict(sorted(json.loads(flash.votes).items(), key=lambda item: item[1])).items()
    elif flash.outcome == True:
        results = dict(sorted(json.loads(flash.votes).items(), key=lambda item: item[1], reverse=True)).items()

    return render(request, "flash/results.html", { "results": results,"flash": flash })


def archive(request):
    return ArchiveListView.as_view()(request)
