# Generated by Django 4.1.5 on 2023-02-04 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_comments_author_comments_listing'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='watchlist',
            constraint=models.UniqueConstraint(fields=('auction_item', 'user'), name='unique_auction_item_per_user'),
        ),
    ]