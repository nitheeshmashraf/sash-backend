import os
import json
from django.template.response import TemplateResponse
import requests
from urllib.parse import unquote
from django.http import HttpResponse
import stripe
stripe.api_key = "sk_test_51J3xXRCJ2mMr1JG8ndwake0gW5f2DrWb5WUKFGSzP7yE0kNxupGNm7i40PMXZP7J8z4Z1hy0YHZL3CZrMHgXV1df002hKTvjv5"

def home(request):
    storefront_url = os.environ.get("STOREFRONT_URL", "")
    dashboard_url = os.environ.get("DASHBOARD_URL", "")
    return TemplateResponse(
        request,
        "home/index.html",
        {"storefront_url": storefront_url, "dashboard_url": dashboard_url},
    )

def confirm_mail(request):
    GRAPHQL_URL = os.environ.get("GRAPHQL_URL", "http://0.0.0.0:8000/graphql/")
    email = unquote(request.GET.get('email'))
    token = request.GET.get('token')
    query = """
    mutation confirmAccount($email:String!,$token:String!){
        confirmAccount(email:$email,token:$token){
            user{
            email
            isActive
            }
            errors{
            message
            }
        }
        }
    """
    URL = GRAPHQL_URL
    json = {
        "query": query,
        "variables": {
            "email": email,
            "token": token
        }
    }
    response = requests.post(url=URL, json=json)
    if response.json()["data"]["confirmAccount"]["user"] is None:
        error = response.json()["data"]["confirmAccount"]["errors"][0]["message"]
        message = error
        return TemplateResponse(
            request,
            "confirm_mail/fail.html",
            {"message":message},
        )
    else :
        message = "Email verified."
        return TemplateResponse(
            request,
            "confirm_mail/success.html",
            {"message":message},
        )

def stripeSavedCards(request):
    data =json.loads(request.body)
    if 'customer_id' in data:
        customer_id = data['customer_id']
        payment_methods = stripe.PaymentMethod.list(
            customer= customer_id,
            type='card'
        )
        print(payment_methods)
        return("success")
    
    return HttpResponse("failed response")

