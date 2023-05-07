from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from sesame.utils import get_token

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
    flash = Flash.objects.get(active=True)
    if flash:
        token = get_token(request.user)
        return render(request, "flash/flash.html", { "flash": flash , "websocket": "ws://localhost:8888", "token": token})
    return FlashCreateView.as_view()(request)