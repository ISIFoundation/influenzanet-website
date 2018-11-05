# Create your views here.
from .utils import render_json
from .api import AscorAPI
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def index(request):

    r = {}

    if request.method == "POST":
        action = request.POST['action']
        api = AscorAPI()
        if action == AscorAPI.ACTION_HANDSHAKE:
            r = api.handshake(request.POST['body'])


    return render_json(request, r)