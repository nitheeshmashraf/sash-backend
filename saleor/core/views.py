import os
import json
from django.template.response import TemplateResponse
import requests
from urllib.parse import unquote
from django.http import HttpResponse
from django.http import JsonResponse
import stripe

def _get_client():
    stripe.api_key = os.environ.get("STRIPE_PRIVATE_KEY")
    return stripe

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
    if request.method == 'POST':
        data =json.loads(request.body)
        stripe = _get_client()
        if 'customer_id' in data:
            customer_id = data['customer_id']
            payment_methods = stripe.PaymentMethod.list(
                customer= customer_id,
                type='card'
            )
            print(payment_methods)
            return JsonResponse(payment_methods)
    
    return HttpResponse("failed response")

