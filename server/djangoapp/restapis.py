import requests
import json
# import related models here
from .models  import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print("kwargs:")
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        #Call get method of requests library with URL and parameters
        if "api_key" in kwargs:
            #authentication GET
            print("it went into the top one")
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        else:
            #no authentication GET
            print("it went into the bottom one")
            response = requests.get(url, params=kwargs)
    except:
        #if any error occurs
        print("Network Exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    #Call get_request with a url parameter
    json_result = get_request(url)
    if json_result:
        #get the row list in JSON as dealers
        dealers = json_result["result"]
        #for each dealer object
        for dealer in dealers:
            #Get its content in 'doc' object
            dealer_doc = dealer["doc"]
            #Create a Car Dealer object with values in 'doc' object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"], id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],   short_name=dealer_doc["short_name"], st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url,dealer_id, **kwargs):
    results = []
    #Call get_request with a url
    json_result = get_request(url, dealerID=dealer_id)
    if "statusCode" not in json_result:
        #get row list in JSON as reviews
        reviews = json_result["body"]["data"]["docs"]
        #for every review
        for review in reviews:
            #create a DealerReview object with values from 'doc' object
            review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"], review=review["review"], purchase_date="", car_make="", car_model="",car_year="", sentiment="", id=review["id"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            if "purchase_date" in review:
                review_obj.purchase_date=review["purchase_date"]
            if "car_make" in review:
                review_obj.car_make=review["car_make"]
            if "car_model" in review:
                review_obj.car_model=review["car_model"]
            if "car_year" in review:
                review_obj.car_year=review["car_year"]

            results.append(review_obj)
    else:
        return 404
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):    
def analyze_review_sentiments(text): 
    url = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/b903bf59-6ce4-43a4-8e34-af2cfd948376"
    api_key = "PH9zyIVYvMYBYP_yxgM6HlLAVCNBRqOf4yaPF9e4B8h2"
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url) 
    response = natural_language_understanding.analyze( text=text ,language="en",features=Features(sentiment=SentimentOptions())).get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return(label) 
