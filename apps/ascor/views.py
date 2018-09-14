# Create your views here.
from .utils import render_json
    
def index(request):
    return render_json(request, {})