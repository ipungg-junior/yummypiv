from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.conf import settings
import os, json, re, time, threading
from datetime import datetime

def get_current_date_time_string():
    current_datetime = datetime.now()
    date_string = current_datetime.strftime("%d/%m/%Y")
    time_string = current_datetime.strftime("%H:%M:%S")
    result_string = f"{date_string} {time_string}"
    return result_string

def ERROR_TAG(txt):
    print(f'\033[91m({get_current_date_time_string()}) ERROR: {txt}\033[0m')    
    
def INFO_TAG(txt):
    print(f'({get_current_date_time_string()}) INFO: {txt}')

def WARNING_TAG(txt):
    print(f'\033[93m({get_current_date_time_string()}) Warning: {txt}\033[0m')

def PRETTIER_TAG(flag, txt):
    print(f'\n({get_current_date_time_string()}) {flag}:\n{txt}')

def INSPECTOR(txt, delay=10):
    print(f'\033[92m({get_current_date_time_string()}) PROCESS HAS STOP FOR INSPECT -> {txt}\033[0m')
    time.sleep(delay)


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            _deny_page = render(request, 'base/403.html')
            _deny_page.status_code = 403
            return _deny_page
        return _wrapped_view
    return decorator


def read_json(filename):
    # Buat path lengkap ke file JSON
    file_path = os.path.join(settings.BASE_DIR, f'{filename}')
    
    # Baca file JSON
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    else:
        print("Error when try unpacking configuration file.")
        return {}
    

def is_valid_phone_number(phone_number):
    pattern = r"^08\d{8,11}$"
    if re.match(pattern, phone_number):
        if (len(str(phone_number)) < 12 > 14):
            return False, None
        return True, phone_number
    return False, None


def is_valid_name(name):
    # Regex untuk memvalidasi nama
    pattern = r"^[A-Za-z\s]+$"
    if re.match(pattern, name):
        # Mengembalikan True dan nama dengan huruf kapital di awal setiap kata
        capitalized_name = ' '.join(word.capitalize() for word in name.split())
        return True, capitalized_name
    return False, None


def idr_to_k(value):
    if value >= 1000:
        return f"{value // 1000}k"
    return str(value)