from functools import wraps
from django.conf import settings
from apps.models import Visitor
import os, json, psutil

total_storage_allocation = settings.STORAGE_ALLOCATION # unit MB

def record_visitor(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')                        
        user_agent = request.META.get('HTTP_USER_AGENT')            
        path = str(request.path)
        Visitor.objects.create(ip_address=ip_address, user_agent=user_agent, path=path)         
        return view_func(request, *args, **kwargs)
    return wrapper

def analyze_storage():
    # Menggunakan os.statvfs untuk mendapatkan informasi tentang sistem file
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(settings.BASE_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    used_project = f"{(total_size*100) / (1024 * 1024):.2f}"
    free_space = f"{((total_storage_allocation - float(used_project)) / 1024):.2f}"
    total_storage = f'{(total_storage_allocation / 1024):.2f}'
    return (total_storage, used_project, free_space)
    