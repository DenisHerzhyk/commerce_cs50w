from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import User,Auction,Bid,Comment


def index(request):
    listings = Auction.objects.filter(is_active=True)
    user_watchlist = []
    if request.user.is_authenticated:
        user_watchlist = request.user.watchlist.all()
    
    for listing in listings:
        listing.is_watchlist = listing in user_watchlist

    return render(request, "auctions/index.html", {
        "listings": listings
    })

def all(request):
    listings = Auction.objects.all()
    user_watchlist = []
    if request.user.is_authenticated:
        user_watchlist = request.user.watchlist.all()
    
    for listing in listings:    
        listing.is_watchlist = listing in user_watchlist
    
    return render(request, "auctions/index.html", {
        "listings": listings
    })

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


def categories(request):
    listings = Auction.objects.values("category").distinct()
    return render(request, "auctions/categories.html", {
        "listings": listings
    })

def category(request, category):
    listings = Auction.objects.filter(category=category)
    user_watchlist = []
    if request.user.is_authenticated:
        user_watchlist = request.user.watchlist.all()

    for listing in listings:
        listing.is_watchlist = listing in user_watchlist

    return render(request, "auctions/category.html", {
        "listings": listings
    })


def listing(request, listing_id):
    if request.method == "GET":
        listing = Auction.objects.get(id=listing_id)
        bids = Bid.objects.filter(listing=listing)
        comments = Comment.objects.filter(listing=listing)

        user_watchlist = []
        if request.user.is_authenticated:
            user_watchlist = request.user.watchlist.all()
        listing.is_watchlist = listing in user_watchlist
        winner = listing.winner
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bids": bids,
            "comments": comments
        })

@login_required
def bid(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            listing = Auction.objects.get(id=listing_id)
            bid_amount = float(request.POST["bid_amount"])

            if (bid_amount > listing.starting_bid):
                Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
                listing.starting_bid = bid_amount
                listing.save()
                bids = Bid.objects.filter(listing=listing)
                comments = Comment.objects.filter(listing=listing)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bids": bids, 
                    "comments": comments
                })
            else:
                bids = Bid.objects.filter(listing=listing)
                comments = Comment.objects.filter(listing=listing)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bids": bids,
                    "comments": comments,
                    "error": "Your bid must be higher than the current bid."
                }) 
        else:
            return HttpResponseRedirect(reverse("login"))
    return HttpResponseNotAllowed(["POST"])

        
@login_required
def comment(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            listing = Auction.objects.get(id=listing_id)
            comment = request.POST["comment"]
            Comment.objects.create(listing=listing, commenter=request.user, comment=comment)
            comments = Comment.objects.filter(listing=listing)
            bids = Bid.objects.filter(listing=listing)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bids": bids,
                "comments": comments
            })
        else:
            return HttpResponseRedirect(reverse("login"))

@login_required
def unactivate(request, listing_id):
    if request.method == "POST":
        listing = Auction.objects.get(id=listing_id)
        if request.user.is_authenticated and request.user == listing.creator:
            listing.is_active = not listing.is_active

            if not listing.is_active:
                highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
                if highest_bid:
                    listing.winner = highest_bid.bidder

            listing.save()

            if listing.is_active:
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error_user": "You are not the creator of this listing."
            })


@login_required
def watchlist(request):
    if request.user.is_authenticated:
        listings = request.user.watchlist.all()
        return render(request, "auctions/watchlist.html", {
            "listings": listings
        })
    else:
        return HttpResponseRedirect(reverse("login"))



@login_required
def watchlist_add(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Auction, id=listing_id)
        if request.user.is_authenticated:
            request.user.watchlist.add(listing)
            return HttpResponseRedirect(reverse("index"))
        return HttpResponseRedirect(reverse("login"))


@login_required
def watchlist_remove(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Auction, id=listing_id)
        if request.user.is_authenticated:
            request.user.watchlist.remove(listing)
            return HttpResponseRedirect(reverse("watchlist"))
        return HttpResponseRedirect(reverse("login"))

def create(request): 
    if request.method == "GET":
        return render(request, "auctions/create.html")
    
    title = request.POST["title"]
    description = request.POST["description"]
    image_url = request.POST["image_url"]
    starting_bid = request.POST["starting_bid"]
    category = request.POST["category"]

    Auction.objects.create(title=title, description=description, image_url=image_url, starting_bid=starting_bid, category=category, creator=request.user, )
    return HttpResponseRedirect(reverse("index"))

