
from urllib2 import urlopen
import json  
def feeback_token(site):
    url = "https://websenti.u707.jussieu.fr/feedback/?action=token&site=%s&version=0.1" % site
    
    try:
        r = urlopen(url)
        result = r.read()
        if r.getcode() == 202:
            result = json.load(result)
            return result
    except: 
        pass
    return None
    
    
    