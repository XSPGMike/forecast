from django.test import TestCase
from django.utils import timezone
import time
import datetime

from .models import brier, weight

# Create your tests here.
class ForecastTestCase(TestCase):
    def test_decent_scores(self):
        self.assertEqual(brier(1, 1), 0)
        self.assertEqual(brier(1, 0), 1)

        started = datetime.datetime(2023, 5, 10, 0, 0, 0)
        pred = datetime.datetime(2023, 5, 20, 0, 0, 0)
        deadline = timezone.now().date() + datetime.timedelta(days=30)
        self.assertEqual(weight(0, pred, started, deadline), 1)
