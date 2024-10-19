from django.urls import path 
from .views import landing, about, services
from viewer.news import News
from viewer.dashboard import Dashboard
from viewer.settings import UserConfigurations, OwnerConfigurations
from viewer.authentication import Authentication
from viewer.content_dashboard import ContentManagement
from services.api import API

urlpatterns = [
    path('', landing, name='landing'),
    path('services/<str:name>/', services, name='services'),
    path('about/', about, name='about'),
    path('dashboard/', Dashboard.as_view(context='main-dashboard'), name='main-dashboard'),
    path('dashboard/partner/', Dashboard.as_view(context='partner-dashboard'), name='partner-dashboard'),
    path('dashboard/content-management/', ContentManagement.as_view(context='content-management'), name='content-management'),
    path('dashboard/partner/create-new/', Dashboard.as_view(context='new-partner'), name='new-partner'),
    path('dashboard/partner/delete/', Dashboard.as_view(context='delete-partner'), name='delete-partner'),
    path('owner-configuration/', OwnerConfigurations.as_view(context='owner-configuration'), name='owner-configuration'),
    path('main-profile/', OwnerConfigurations.as_view(context='main-profile'), name='main-profile'),
    path('user-configuration/', UserConfigurations.as_view(context='user-list'), name='user-list'),
    path('login/', Authentication.as_view(context='login'), name='login'),
    path('logout/', Authentication.as_view(context='logout'), name='logout'),
    path('register/', Authentication.as_view(context='register'), name='register'),

    # API Based
    path('api/client-inbox/', API.as_view(context='api-client-inbox'), name='api-client-inbox'),
    path('api/visitor/', API.as_view(context='api-visitor'), name='api-visitor'),
    path('api/reporter/', API.as_view(context='api-reporter'), name='api-reporter'),
    path('api/news/delete/', API.as_view(context='api-news-delete'), name='api-news-delete'),
    path('api/social-link/', API.as_view(context='api-social-link'), name='api-social-link'),
    path('api/edit-user/', API.as_view(context='api-edit-user'), name='api-edit-user'),
    path('api/content-management/homepage-upper/', API.as_view(context='api-update-homepage-upper'), name='api-update-homepage-upper'),
]
