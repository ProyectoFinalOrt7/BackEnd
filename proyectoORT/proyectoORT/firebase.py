from django.contrib.auth import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, BadRequest, ObjectDoesNotExist
from democracia.models.auth import Ciudadano
import firebase_admin
import json
import requests
import base64
from functools import wraps
from firebase_admin import credentials, firestore, auth
from django.conf import settings
from requests.api import request
from requests.models import requote_uri

# Instantiate Flask extensions
cred = credentials.Certificate(settings.FIREBASE_CONFIG_FILE)
firebase = firebase_admin.initialize_app(cred)
api_key = json.load(open(settings.FIREBASE_CONFIG_FILE,"r"))["apiKey"]
fs_client = firestore.client()

def serialize_firebase_user(user):
    return {
        'email': user.email,
        'name': user.display_name
    }

def list_all_users():
    page = auth.list_users()
    users = [ serialize_firebase_user(user) for user in page.users ]
    page = page.get_next_page()
    while page:
        users.extend([ serialize_firebase_user(user) for user in page.users ])
        page = page.get_next_page()
    return users

def create_user(email, password):
    return auth.create_user(
               email=email,
               password=password
        )

def generate_token(email, password):
    request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(request_ref, headers=headers, data=data)
    return request_object.json()['idToken']

def get_user_from_firebase(fb_user):
    try:
        ciudadano = Ciudadano.objects.get(email=fb_user['email'])
    except ObjectDoesNotExist:
        try:
            user = User.objects.get(username=fb_user['email'])
        except ObjectDoesNotExist:
            user = User.objects.create_user(
                username=fb_user['email'],
                email=fb_user['email'],
                password='Password123$'
                )
            user.save()
        ciudadano = Ciudadano(
                user=user,
                nombre=fb_user['email'],
                email=fb_user['email'],
                firebaseId=fb_user['user_id']     
                )
        ciudadano.save()
    return ciudadano.user
            

def login_required():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if 'Authorization' in request.headers:
                auth_method, value = request.headers['Authorization'].split()
                if auth_method == 'Token':
                    fb_user = auth.verify_id_token(value)
                    request.user = get_user_from_firebase(fb_user)
                else:
                    raise BadRequest(f'Authentication method not recognized {auth_method}')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator