from django.shortcuts import render
from django.conf import settings
from apps.models import Partner, Article, OwnerProfile

# Logger information object
import logging
logger = logging.getLogger('yummypiv')

def landing(request):
    partner_list = Partner.objects.all()
    news_list = Article.objects.order_by('-created_at')[:7]
    all_profile = OwnerProfile.objects.all()
    ctx = {}            
    for profile_item in all_profile:
        ctx[profile_item.info] = profile_item.content     
    
    ctx['partner_list'] = partner_list
    ctx['news_list'] = news_list
    
    resp = render(template_name='index.html', request=request, context=ctx)
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    logger.info(f'{request.META.get('REMOTE_ADDR')} - {request.META.get('HTTP_USER_AGENT')} - Landing page')
    return resp

def services(request, name):
    news_list = Article.objects.order_by('-created_at')[:7]
    all_profile = OwnerProfile.objects.all()
    ctx = {}            
    for profile_item in all_profile:
        ctx[profile_item.info] = profile_item.content     
    ctx['news_list'] = news_list
    
    my_template = str(name).replace('-', '_')
    ctx['description'] = my_template.replace('_', ' ').title()
    
    resp = render(template_name=f'services_partial/{my_template}.html', request=request, context=ctx)
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    logger.info(f'{request.META.get('REMOTE_ADDR')} - {request.META.get('HTTP_USER_AGENT')} - Service {my_template} page landing')
    return resp

def about(request):
    partner_list = Partner.objects.all()
    news_list = Article.objects.order_by('-created_at')[:7]
    all_profile = OwnerProfile.objects.all()
    ctx = {}            
    for profile_item in all_profile:
        ctx[profile_item.info] = profile_item.content     
    
    ctx['partner_list'] = partner_list
    ctx['news_list'] = news_list
    
    resp = render(template_name='about.html', request=request, context=ctx)
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    logger.info(f'{request.META.get('REMOTE_ADDR')} - {request.META.get('HTTP_USER_AGENT')} - About page')
    return resp