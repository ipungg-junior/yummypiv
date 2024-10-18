from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from services.news import most_viewed_article
from services.utils import role_required
from apps.models import OwnerProfile
from django.utils import timezone
from datetime import timedelta


# Logger information object
from services.logger import logger


@method_decorator(role_required(['root', 'admin', 'staff']), name='dispatch')
class ContentManagement(View):
    context = ''

    def get(self, request, *args, **kwargs):

        if (self.context == 'content-management'):
            all_profile = OwnerProfile.objects.all()
            ctx = {}            
            
            for profile_item in all_profile:
                ctx[profile_item.info] = profile_item.content    
                
            return render(request, 'content_management.html', context=ctx)