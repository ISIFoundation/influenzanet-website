# Create your views here.
from .utils import render_json
from .api import AscorAPI, APIError
from django.views.decorators.csrf import csrf_exempt
from . import ASCOR_DEBUG

@csrf_exempt
def index(request):

    r = {}
    status = 501

    if request.method == "POST":
        action = request.POST['action']
        api = AscorAPI()
        try:
                if action == AscorAPI.ACTION_HANDSHAKE:
                        api_session = api.handshake(request.POST['body'])
                        request.session['api_session'] = api_session
                        r['ok'] = True
                        status = 200
        except APIError, e:
                r['error'] = True
                r['message'] = "Error during handshake"
                if ASCOR_DEBUG:
                        r['exception'] = e.to_json()

    return render_json(request, r, status=status)