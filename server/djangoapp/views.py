from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf, post_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)



# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        #get username and password from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        #check if can authenticate
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:registration')
    else:
        return redirect('djangoapp:registration')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        #get sign up info
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist=False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is a new user".format(username))
        #create new user
        if not user_exist:
            user = User.objects.create_user(username=username,password=password,first_name=first_name,last_name=last_name)
            login(request,user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context={}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7ab6e43a-6ec0-4080-a0b3-481deeeb1bc1/djangoapp/get_all_dealerships.json"
        #get dealers from the URL
        context["dealership_list"]=get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = '<br>'.join([dealer.short_name for dealer in dealerships])
        #return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7ab6e43a-6ec0-4080-a0b3-481deeeb1bc1/djangoapp/get_reviews.json?id=" + str(dealer_id)
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        if reviews==404:
            review_contents="This dealership has no reviews."
        else:
            review_contents = '<br>'.join([review.review + ": " + review.sentiment for review in reviews])
        return HttpResponse(review_contents)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    if request.method == "GET":
        context={}
        context["dealer_id"]=dealer_id
        return render(request, 'djangoapp/add_review.html', context)
    
    if request.method == "POST":
        # check if user is authenticated
        if request.user.is_authenticated:
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/7ab6e43a-6ec0-4080-a0b3-481deeeb1bc1/djangoapp/post_review"
            review = {
                "id": 1114,
                "name": request.POST['name'],
                "dealership": 15,
                "review": request.POST['review'],
                "purchase": False,
                "another": "field",
                "purchase_date": "02/16/2021",
                "car_make": "Audi",
                "car_model": "Car",
                "car_year": 2021
            }
            json_payload = {}
            json_payload["review"] = review
            post_request(url, json_payload, dealerId=dealer_id)
        return redirect("djangoapp:index")
