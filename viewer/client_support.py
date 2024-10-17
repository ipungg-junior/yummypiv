from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from services.news import most_viewed_article
from services.utils import role_required
from apps.models import ClientInbox
from django.utils import timezone
from datetime import timedelta


# Logger information object
from services.logger import logger


@method_decorator(role_required(['root', 'admin', 'staff']), name='dispatch')
class ClientSupport(View):
    context = ''

    def get(self, request, *args, **kwargs):

        if (self.context == 'client-support-dashboard'):
            ctx = {}
            inbox_list = ClientInbox.objects.order_by('-created_at')
            ctx['inbox_list'] = inbox_list
            return render(request, 'support_dashboard.html', context=ctx)