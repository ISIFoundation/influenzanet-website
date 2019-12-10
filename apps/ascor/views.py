# Create your views here.

from django.shortcuts import redirect
from .utils import render_json
from .api import AscorAPI, APIError
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.models import User
from . import ASCOR_DEBUG
import json

from .models import Session

from apps.survey.household import SurveyHousehold  #class SurveyHousehold ,  get_household(request)
from apps.survey.models import SurveyUser

@csrf_exempt
def index(request):
    response = {}
    status = 501
    print("start index")
    if request.method == "POST":
        try:
            #TODO : ameliorer action tout le temps? body parfois?
            POST_data = json.loads(request.raw_post_data)
            if "body" in POST_data :
                body = POST_data['body']
            else:
                body =""

            if "action" in POST_data :
                action = POST_data['action']
            else:
                action =""
            api = AscorAPI()

            #if "action" in POST_data.keys() and action == api.ACTION_HANDSHAKE:
            if action == api.ACTION_HANDSHAKE:
                    api_session = api.handshake(request, body)
                    request.session['api_session'] = api_session   # allow to persist parameters across requests and also persists cookies across all requests made from the Session instance
                    response = api_session
                    status= 200
            else :
                if "idSession" in POST_data.keys() :
                    idSession = POST_data['token']
                    Session = Session.objects.get(IDSession = idSession)
                #decrypter body => get "action" puis faire l'action
        except APIError, e:
                response['error'] = True
                response['message'] = "Error during handshake"
                if ASCOR_DEBUG:
                    response['exception'] = e.to_json()
    return render_json(request, response, status=status)

@csrf_exempt
def user_participants(request):

    POST_data = json.loads(request.raw_post_data)
    IDSession = POST_data['']
    response = {}
    status = 501
    #print(request.method)

    #print ("Session keys : "+ str(request.session.keys()))
    try:
        session = Session.objects.get(IDSession = IDSession)
        #session.HMACkey
        user = User.objects.get(username=str(session.Username))
        request.user = user


        household = SurveyHousehold.get_household(request)

        print("SurveyHousehold : "+str(household.participants)+ " nb : "+str(household.count()))

        api = AscorAPI()
        response = api.listing_users(request, session, household)
        status = 200
    except APIError, e:
            response['error'] = True
            response['message'] = "Error during participants listing"

    return render_json(request, response, status=status)

def formulaire(request):
    POST_data = json.loads(request.raw_post_data)
    hs = 500 #doit recuperer hs
    body = POST_data['body']
    request.session['api_session']
    api = AscorAPI()
    api.get_body(body, hs)
    body.action
    response = {}
    status = 501
    action = POST_data['action']
    if request.method == "POST":
        if action == AscorAPI.ACTION_HANDSHAKE:
            status= 200
    return render_json(request, response, status=status)

def user_participant(request):
    response = {}
    status = 501
    return render_json(request, response, status=status)