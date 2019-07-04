from django.http import HttpResponse
import json

def render_json(request, data, headers=None, status=None):
    response = HttpResponse(json.dumps(data), content_type="application/json", status=status)
    if headers is not None:
        if isinstance(headers, dict):
            for k,v in headers:
                response[k] = v
    return response