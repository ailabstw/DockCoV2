import os

def export_vars(request):
    data = {}
    data['COVID19_WEB_APP'] = os.getenv('COVID19_WEB_APP')
    return data
