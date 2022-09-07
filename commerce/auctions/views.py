from typing import List
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        #  Excluding the repeat category
        "categories": Listing.objects.values('category').distinct().exclude(category__exact='')
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

@login_required
def create_listing(request):
    context = {}
    listing_form = ListingForm(request.POST or None, request.FILES or None)

    if listing_form.is_valid():
        listing_form.save()
    context['listing_form'] = listing_form        
    return render(request, "auctions/create.html", context)

def listing(request, auction_id):
    try:
        listing = Listing.objects.get(pk=auction_id)
    except Listing.DoesNotExist:
        raise Http404("Product not found.")
    return render(request, "auctions/listing.html", {
        "auction": listing,
        'user': request.user
    })
        
@login_required
def add_watchlist(request, auction_id):
    if request.method == 'POST':
        item = Listing.objects.get(pk=auction_id)
        watching = User.objects.get(id=request.user.id)
        watchlist_list = Watchlist(user=watching, item=item)
        item_in = Watchlist.objects.filter(user=request.user.id, item=item)
        if item_in.exists():
            item_in.delete()             
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            watchlist_list.save() 
            return HttpResponseRedirect(reverse("watchlist"))
    return render(request, "auctions/watchlist.html", {
        "watchlists": item_in.all()
        })

@login_required
def watchlist(request):
   return render(request, "auctions/watchlist.html", {
        "watchlists": Watchlist.objects.filter(user=request.user.id)
    })

@login_required
def bid_update(request, auction_id):
    if request.method == 'POST':
        current_one = Listing.objects.get(pk=auction_id)
        current_bid = current_one.starting_bid
        if request.user.username:
            bid_num = float(request.POST.get('amount'))
            if bid_num >= current_bid:
                new_bid = Listing.objects.get(pk=auction_id)
                new_bid.starting_bid = bid_num
                bid = Bid(user=request.user, auction=new_bid, amount=bid_num)
                bid.save()
                messages.success(request, "Successfully! now you bid is the higest!")
                return HttpResponseRedirect(reverse("listing", kwargs={'auction_id': auction_id,}))
            else:
                messages.error(request, "Your bid must be higher than the current one.")
                return HttpResponseRedirect(reverse("listing", kwargs={'auction_id': auction_id,}))
    return HttpResponseRedirect(reverse("listing", kwargs={'auction_id': auction_id,}))
    
@login_required
def close_bid(request, auction_id):
    if request.method == "POST":
        active_list = Listing.objects.get(pk=auction_id)
        active_list.active = False 
        bid_count = Bid.objects.filter(auction=auction_id).count()
        if bid_count > 0:
            lastest_bid = Listing.current_price(auction_id)
            last_one = lastest_bid['amount__max']
            the_winner = Bid.objects.get(auction=auction_id, amount=last_one)
            active_list.winner = the_winner.user
            active_list.save()
            messages.success(request, "Successfully close your bid!")
            return HttpResponseRedirect(reverse("index"))
        else:
            active_list.winner = None
            return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("listing", kwargs={'auction_id': auction_id,}))

    
@login_required
def comment(request, auction_id):
    if request.method == "POST":
        auction = Listing.objects.get(pk=auction_id)
        comment_text = request.POST['comment']
        comment = Comment(user=request.user, auction=auction, text=comment_text)
        comment.save()
        return HttpResponseRedirect(reverse("listing", kwargs={'auction_id': auction_id,}))

    
def category(request, category):
    list_category = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        'category': category,
        'list_category': list_category
    })