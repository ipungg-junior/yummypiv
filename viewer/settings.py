from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from apps.models import Users, OwnerProfile
from django.utils.decorators import method_decorator
from services.firebase import firebase_upload
from services.utils import role_required
from django.http import JsonResponse
from apps.models import Users


# Logger information object
import logging
logger = logging.getLogger('yummypiv')


@method_decorator(role_required(['root', 'admin']), name='dispatch')
class UserConfigurations(View):
    
    context = ''

    def get(self, request, *args, **kwargs):
        
        if (self.context == 'user-list'):
            user_list = Users.objects.all()
            ctx = {
                'user_list' : user_list
            }
            resp = render(template_name='user_list.html', request=request, context=ctx)
            return resp
        
    def post(self, request, *args, **kwargs):
        
        if (self.context == 'user-list'):
            try:
                action = request.POST['action']
                selected_user_id = request.POST['user-id']
                if (action == 'delete'):
                    try:
                        selected_user_id = Users.objects.get(id=selected_user_id)
                        selected_user_id.delete()
                        logger.info(f'User {selected_user_id.username} has been deleted!')                        
                        return JsonResponse({'status': True, 'data':{'msg': 'User deleted.'}})
                    except:
                        logger.error(f'Error when deleted user id {selected_user_id}, User does not exist!')                        
                        return JsonResponse({'status': False, 'data':{'msg': 'Error on search user id, please contact administrator!'}})
                if (action == 'edit'):
                    try:
                        selected_user_id = Users.objects.get(id=selected_user_id)
                        email_user = selected_user_id.email
                        role_user = selected_user_id.role                        
                        base_role = Users.ROLE_CHOICES
                        logger.info(f'Completed get data for editing user {selected_user_id.username}')                        
                        return JsonResponse({'status': True, 'data':{'email': email_user, 'base_role': base_role, 'selected_role': role_user}})
                    except:
                        logger.error(f'Error when editing user id {selected_user_id}, User does not exist!')                        
                        return JsonResponse({'status': False, 'data':{'msg': 'Error on search user id, please contact administrator!'}})
            except:
                logger.error(f'Error web api on "user-list" context with POST method, form data corrupted!')                        
                return JsonResponse({'status': False, 'data':{'msg': 'Wrong foem data uploaded!'}})
                
        


@method_decorator(role_required(['root', 'admin']), name='dispatch')
class OwnerConfigurations(View):
    
    context = ''

    def get(self, request, *args, **kwargs):
        
        if (self.context == 'owner-configuration'):
            ctx = {}
            all_profile = OwnerProfile.objects.all()
            
            for profile_item in all_profile:
                ctx[profile_item.info] = profile_item.content                        
                
            resp = render(template_name='owner_configuration.html', request=request, context=ctx)
            return resp

    def post(self, request, *args, **kwargs):
    
        if (self.context == 'main-profile'):
            
            for key, value in request.POST.items():
                key_correction = str(key).replace('-', '_')
                try: 
                    exist_data = OwnerProfile.objects.get(info=key_correction)
                    exist_data.content = value
                    exist_data.save()
                except Exception as no_data:
                    new_data = OwnerProfile(info=key_correction, content=value)
                    new_data.save()

            if (request.FILES.get('background-image')):

                img = request.FILES.get('background-image')

                if (img.name).endswith('.png'):
                    sts, msg = firebase_upload('company', img, 'background-image', ct='png')                    
                if (img.name).endswith('.jpg'):
                    sts, msg = firebase_upload('company', img, 'background-image', ct='jpg')                    
                if (img.name).endswith('.jpeg'):
                    sts, msg = firebase_upload('company', img, 'background-image', ct='jpeg')                    
                if (img.name).endswith('.webp'):
                    sts, msg = firebase_upload('company', img, 'background-image', ct='webp')
                
                if sts:
                    try:
                        exist_data = OwnerProfile.objects.get(info='background_image')
                        exist_data.content = msg
                        exist_data.save()
                    except Exception as no_data:
                        new_data = OwnerProfile(info='background_image', content=msg)
                        new_data.save()
                else:
                    return JsonResponse({'status': True, 'data':{'msg': 'Update success, but background-image corrupt!'}})              
                
            return JsonResponse({'status': True, 'data':{'msg': 'Update success'}})