# Generated by Django 4.2 on 2023-04-21 23:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forecasts", "0005_alter_forecast_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forecast",
            name="title",
            field=models.CharField(max_length=40),
        ),
    ]
