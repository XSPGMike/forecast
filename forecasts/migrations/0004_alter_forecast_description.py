# Generated by Django 4.2 on 2023-04-21 23:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forecasts", "0003_alter_forecast_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forecast",
            name="description",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
