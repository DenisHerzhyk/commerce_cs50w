# Generated by Django 5.2.4 on 2025-07-16 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_bid_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='is_watchlist',
            field=models.BooleanField(default=False),
        ),
    ]
