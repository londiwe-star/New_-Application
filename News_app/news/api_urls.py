"""
API URL configuration for the news application.

This module defines all API URL patterns for the REST API.
"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('token/', obtain_auth_token, name='api_token_auth'),
    
    # Articles
    path('articles/subscribed/', api_views.SubscribedArticlesAPIView.as_view(), name='subscribed_articles'),
    path('articles/publisher/<int:pk>/', api_views.PublisherArticlesAPIView.as_view(), name='publisher_articles'),
    path('articles/journalist/<int:pk>/', api_views.JournalistArticlesAPIView.as_view(), name='journalist_articles'),
    
    # Publishers
    path('publishers/', api_views.PublisherListAPIView.as_view(), name='publisher_list'),
]


