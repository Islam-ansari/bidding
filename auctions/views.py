from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *

from .models import User


def index(request):
    return render(request, "auctions/index.html",{
        "auction_listings": AuctionListing.objects.all(),
    })

@login_required(login_url="login")
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all(),
        })
    else:
        #if user submits form/ access form through POST method
        #get data from the form
        product_name = request.POST["product_name"]
        price = request.POST["price"]
        image_url = request.POST["image_url"]
        description = request.POST["description"]
        category = request.POST["category"]
        #create bid object
        bid = Bid(bid=float(price), user=request.user)
        bid.save()
        #since category is the foreign key so can't directly save it, so we are getting Category instance here
        categoryData = Category.objects.get(category_name = category)

        #insert data in the database
        new_listing = AuctionListing(
            product_name = product_name,
            product_price = bid,
            image = image_url,
            description = description,
            category = categoryData,
            owner = request.user
        )

        new_listing.save()
        return HttpResponseRedirect(reverse(index))

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
    })

# function related perticular category like "toys", 'electronics'
def category(request, name):
    category_data = Category.objects.get(category_name = name)
    auctions = AuctionListing.objects.filter(
        category = category_data
    )
    return render(request, "auctions/related_category.html",{
        "auctions": auctions,
        "title": name
    })

def listing(request, id):
    # if user logged in, check if auction in the watchlist
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
    listing_item = AuctionListing.objects.get(pk=id)
    isOwner = request.user.username == listing_item.owner.username
    allComments = Comments.objects.filter(listing=listing_item)
    print(request.user == listing_item.product_price.user)
    return render(request, "auctions/listing.html",{
            "listing_item": listing_item,
            "allComments": allComments,
            "isOwner": isOwner,
            "user": request.user
    })

# //////////////////////////////////////////////////////add/remove/displayWatchlist/////////////////////////////////////////////////////////
def removefromWatchlist(request, id):
    item = AuctionListing.objects.get(pk=id)
    Watchlist.objects.filter(user=request.user, auction_item=item).delete()
    return redirect('listing', id=id)

def addtoWatchlist(request, id):
    item = AuctionListing.objects.get(pk=id)
    watchlist_item = Watchlist(
        auction_item = item,
        user = User.objects.get(id=request.user.id)
    )
    try:
        watchlist_item.save()
    except IntegrityError:
        return HttpResponse("Listing already exists in your watchlist")
    return redirect('listing', id=id)

@login_required(login_url="login")
def display_watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/display.html",{
        "watchlist_items": watchlist_items,
    })


#////////////////////////////////////////////////////////Close Auction//////////////////////////////////////////////////////////////////////
@login_required(login_url="login")
def closeAuction(request, id):
    listingData = AuctionListing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    allComments = Comments.objects.filter(listing=listingData)
    user_won = False
    if request.user == listingData.product_price.user:
        user_won = True
    return render(request, "auctions/listing.html",{
            "listing_item": listingData,
            "allComments": allComments,
            "isOwner": isOwner,
            "updated": True,
            "message_bid": "Warning! You've closed this auction!",
            "user_won": user_won,
    })

# /////////////////////////////////////////////////Comment//////////////////////////////////////////////////////////////////////////////////
@login_required(login_url="login")
def addComment(request, id):
    message = request.POST["message"]
    listing = AuctionListing.objects.get(pk=id)
    user = request.user

    newComment = Comments(
        author = user,
        listing = listing,
        message = message,
    )
    newComment.save()
    return redirect('listing', id=id)

#////////////////////////////////////////////////////Bid//////////////////////////////////////////////////////////////////////////
@login_required(login_url="login")
def addBid(request,id):
    newBid= float(request.POST["newBid"])
    listing_item = AuctionListing.objects.get(pk=id)
    isOwner = request.user.username == listing_item.owner.username
    if newBid > listing_item.product_price.bid:
        #update the bid value
        updateBid = Bid(user=request.user, bid=newBid)
        updateBid.save()
        #somehow update the .price.bid with new value is not working so since price is foreign key to the Bid so we made it equal to updated bid instance
        listing_item.product_price = updateBid
        listing_item.save()
        allComments = Comments.objects.filter(listing=listing_item)
        return render(request, "auctions/listing.html",{
                "listing_item": listing_item,
                "message": "Bid placed Successfully",
                "updated": True,
                "allComments": allComments,
                "isOwner": isOwner
        })
        # return redirect('listing', id=id)
    else:
        allComments = Comments.objects.filter(listing=listing_item)
        return render(request, "auctions/listing.html",{
                "listing_item": listing_item,
                "message": "Bid should be higher than current price!",
                "updated": False,
                "allComments": allComments,
                "isOwner": isOwner
        })
        # return redirect('listing', id=id)


#////////////////////////////////////////////////////Login/Logout//////////////////////////////////////////////////////////////////////////
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#////////////////////////////////////////////////////Register//////////////////////////////////////////////////////////////////////////
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#////////////////////////////////////////////////////Bid//////////////////////////////////////////////////////////////////////////
def greeting(request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is None:
            return render(request, "auctions/greeting.html")
