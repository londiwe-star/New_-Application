"""
Serializers for the REST API.

This module contains Django REST Framework serializers for
serializing model data to JSON format for API responses.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article, Newsletter, Publisher

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Excludes sensitive information like password.
    """
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                'role', 'role_display', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        """Return user's full name or username if not available."""
        return obj.get_full_name() or obj.username


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher model.
    
    Includes basic publisher information.
    """
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model.
    
    Includes nested author and publisher information.
    """
    
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    is_independent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'publisher', 
                  'is_approved', 'approved_by', 'is_independent',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_approved', 'approved_by']


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter model.
    
    Includes nested author and publisher information.
    """
    
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    is_independent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'content', 'author', 'publisher', 
                  'is_independent', 'created_at']
        read_only_fields = ['id', 'created_at']


