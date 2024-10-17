from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.contrib.auth import authenticate, login, get_user_model, logout
from apps.models import Users
from django.http import JsonResponse
from services.mail_service import send_mail

# Logger information object
import logging
logger = logging.getLogger('yummypiv')

class Authentication(View):
    
    context = ''

    def get(self, request, *args, **kwargs):
        
        if (self.context == 'login'):
            if (request.user.is_authenticated):
                return redirect('main-dashboard')
            logger.info(f'Memuat laman login dashboard')
            resp = render(template_name='login.html', request=request)
            return resp
        if (self.context == 'logout'):
            logger.info(f'LOGOUT SESSION {request.user}')
            logout(request)
            return redirect('landing')
        
    def post(self, request, *args, **kwargs):
        
        if (self.context == 'login'):
            username = request.POST.get('username')
            passw = request.POST.get('password')
            user = authenticate(request=request, username=username, password=passw)
            if user:                
                try:
                    login(request, user)
                    logger.info(f'Login successfully from {username}')
                    return JsonResponse({'status': True, 'data':{'msg': 'Login berhasil'}})     
                except Exception as login_eror:
                    logger.error(f'Percobaan login gagal {login_eror}')
                    return JsonResponse({'status': False, 'data':{'msg': 'Internal server error'}})     
            else:
                logger.error(f'Login gagal username/pass salah {username}')
                send_mail(receipt="ipungg.id@gmail.com", subject="Login failed systema dashboard")
                logger.info(f'Trying send mail alert login failed.')
                return JsonResponse({'status': False, 'data':{'msg': 'User/Password salah'}})     


        if (self.context == 'register'):
            username = request.POST.get('username')
            passw = request.POST.get('password')
            confirm_passw = request.POST.get('password-confirm')
            role = request.POST.get('role')
            email = request.POST.get('email')
            logger.info(f'Memulai daftar user baru {username}-{role}')
            
            user_model = get_user_model()
            if (len(username) > 7 and len(passw) > 8):        
                try:
                    new_user = user_model.objects.create_user(username=username, password=passw)
                    new_user.role = role
                    new_user.email = email
                    new_user.save()
                    logger.info(f'Akun berhasil didaftarkan {username}-{role}')
                    return JsonResponse({'status': True, 'data':{'msg': 'Login berhasil'}})
                except Exception as failed_create_user:
                    logger.error(f'Gagal membuat user baru {failed_create_user}')
                    return JsonResponse({'status': False, 'data':{'msg': 'Server maintenance (500 Internal Server)'}})
            else:
                logger.error(f'Karakter kurang atau invalid {username}')
                return JsonResponse({'status': False, 'data':{'msg': 'Username/password terlalu pendek'}})
