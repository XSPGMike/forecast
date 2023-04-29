from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import time

def brier(outcome, prediction):
    return (outcome - prediction) ** 2

def ts(d):
    return time.mktime(d.timetuple())

def weight(br, pred, started, deadline):
    x = (1 - br) + 0.1
    y = (pred.timestamp() - started.timestamp()) / (ts(deadline) - started.timestamp())
    return x*(y**2)

# Create your models here.
class Forecast(models.Model):
    title = models.CharField(max_length=60)
    deadline = models.DateField()
    description = models.CharField(max_length=500, null=True, blank=True)
    outcome = models.BooleanField(null=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    private = models.BooleanField(default=False)
    hidden_to = models.ManyToManyField(User, related_name="hidden_to", blank=True)

    def __str__(self):
        return self.title

    def vote_count(self):
        return self.vote_set.count()

    def vote_avg(self):
        avg = self.vote_set.aggregate(models.Avg("vote"))["vote__avg"]
        if avg:
            avg = round(avg, 2)
        return avg

    def expired(self):
        return self.deadline < timezone.now().date()

    def ended(self):
        return self.expired() and self.outcome is not None

    def scores(self):
        if self.outcome is None:
            return []

        scores = {}
        for vote in self.vote_set.all():
            br = brier(self.outcome, vote.vote / 100)
            wh = weight(br, vote.created_at, self.created_at, self.deadline)
            if not scores.get(vote.user.username):
                scores[vote.user.username] = { 'brier': br * wh, 'weight': wh }
            else:
                scores[vote.user.username]['brier'] += br * wh
                scores[vote.user.username]['weight'] += wh

        final_scores = []
        for user in scores:
            final_scores.append([user, round(scores[user]['brier'] / scores[user]['weight'], 4)])

        return sorted(final_scores, key=lambda x: x[1])


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    forecast = models.ForeignKey(Forecast, on_delete=models.CASCADE)
    vote = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.vote)
