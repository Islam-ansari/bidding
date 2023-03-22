from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder", null=True)

    def __str__(self):
        return f"${self.bid}"

class Category(models.Model):
    category_name = models.CharField(max_length=128, null=True)
    category_details = models.TextField(max_length=128, null=True)

    def __str__(self):
        return self.category_name

    # here we can also type simply count_active_auction = AuctionListing.objects.filter... but it will cause performance issue, because the method will run every time property is assessed
    @property
    def count_active_auctions(self):
        return AuctionListing.objects.filter(category=self).count()


class AuctionListing(models.Model):
    product_name = models.CharField(max_length=128)
    product_price = models.ForeignKey(Bid, on_delete=models.CASCADE, null=True, related_name="bid_price", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing", null=True, blank=True)
    image = models.URLField()
    description = models.TextField()
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_category")
    users = models.ManyToManyField(User, through='Watchlist', related_name='items')

    #this __str__ fxn will show the name of auction list instead of showig AuctionListing Object
    def __str__(self):
        return self.product_name

class Watchlist(models.Model):
    auction_item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlist_item")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    # to avoid getting duplicate items in watchlist
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["auction_item", "user"], name="unique_auction_item_per_user")
        ]

    def __str__(self):
        return f"{self.auction_item} on user {self.user} watchlist"

class Comments(models.Model):
    # we put null=True to avoid error to chose any default value
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user", null=True)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment_on_listing", null=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} commented on {self.listing}"

