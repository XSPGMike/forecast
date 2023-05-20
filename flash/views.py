from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
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

@login_required
def index(request):
    flash = Flash.objects.filter(active=True).first()
    if flash:
        return redirect(f"/flash/{flash.uuid}")
    return FlashCreateView.as_view()(request)

@login_required
def flash(request, uuid):
    flash = Flash.objects.filter(uuid=uuid).first()

    if not flash:
        return redirect("/")
    if flash.active:
        token = get_token(request.user)
        return render(request, "flash/flash.html", { "flash": flash , "token": token })

    results = dict(sorted(json.loads(flash.votes).items(), key=lambda item: item[1])).items()
    return render(request, "flash/results.html", { "results": results,"flash": flash })
