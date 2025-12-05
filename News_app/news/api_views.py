"""
API views for the REST API.

This module contains Django REST Framework API views for
handling API requests and responses.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Article, Newsletter, Publisher, User
from .serializers import ArticleSerializer, NewsletterSerializer, PublisherSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API responses.
    
    Limits results to 20 items per page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SubscribedArticlesAPIView(APIView):
    """
    API view to get articles from user's subscribed publishers and journalists.
    
    Returns articles from:
    - Publishers the user is subscribed to
    - Journalists the user is subscribed to
    
    Requires authentication.
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        """
        GET request handler.
        
        Returns paginated list of articles from subscribed sources.
        """
        user = request.user
        
        # Get subscribed publishers and journalists
        subscribed_publishers = user.publisher_subscriptions.all()
        subscribed_journalists = user.journalist_subscriptions.all()
        
        # Get articles from subscribed sources (only approved)
        articles = Article.objects.filter(
            is_approved=True
        ).filter(
            Q(publisher__in=subscribed_publishers) |
            Q(author__in=subscribed_journalists)
        ).select_related('author', 'publisher', 'approved_by').order_by('-created_at')
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(articles, request)
        
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublisherArticlesAPIView(APIView):
    """
    API view to get articles by publisher ID.
    
    Returns all approved articles from a specific publisher.
    Requires authentication.
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, pk):
        """
        GET request handler.
        
        Args:
            pk: Publisher primary key
        
        Returns paginated list of articles from the publisher.
        """
        publisher = get_object_or_404(Publisher, pk=pk)
        
        # Get approved articles from this publisher
        articles = Article.objects.filter(
            publisher=publisher,
            is_approved=True
        ).select_related('author', 'publisher', 'approved_by').order_by('-created_at')
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(articles, request)
        
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JournalistArticlesAPIView(APIView):
    """
    API view to get articles by journalist ID.
    
    Returns all approved articles from a specific journalist.
    Requires authentication.
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, pk):
        """
        GET request handler.
        
        Args:
            pk: Journalist (User) primary key
        
        Returns paginated list of articles from the journalist.
        """
        journalist = get_object_or_404(User, pk=pk, role=User.Role.JOURNALIST)
        
        # Get approved articles from this journalist
        articles = Article.objects.filter(
            author=journalist,
            is_approved=True
        ).select_related('author', 'publisher', 'approved_by').order_by('-created_at')
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(articles, request)
        
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublisherListAPIView(APIView):
    """
    API view to list all publishers.
    
    Returns list of all publishers in the system.
    Requires authentication.
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """GET request handler. Returns list of all publishers."""
        publishers = Publisher.objects.all().order_by('name')
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


