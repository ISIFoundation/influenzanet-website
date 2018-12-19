# Create your views here.
from .utils import render_json
from .api import AscorAPI, APIError
from django.views.decorators.csrf import csrf_exempt
from . import ASCOR_DEBUG
import json

@csrf_exempt
def index(request):

    response = {}
    status = 501


    #raise KeyError(request.POST)

    if request.method == "POST":
        try:
            POST_data = json.loads(request.raw_post_data)
            body = POST_data['body']
            #body['RSA4096']
            #
            action = POST_data['action']
            api = AscorAPI()

            if action == AscorAPI.ACTION_HANDSHAKE:
                    api_session = api.handshake(body['RSA4096'])
                    request.session['api_session'] = api_session   # allow to persist parameters across requests and also persists cookies across all requests made from the Session instance
                    response = api_session
                    status = 200
        except APIError, e:
                response['error'] = True
                response['message'] = "Error during handshake"
                if ASCOR_DEBUG:
                    response['exception'] = e.to_json()

    return render_json(request, response, status=status)
