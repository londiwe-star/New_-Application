"""
Admin configuration for the news application.

This module contains Django admin customizations for all models,
including list displays, filters, search fields, and custom actions.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import User, Publisher, Article, Newsletter


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    
    Extends BaseUserAdmin with role-specific fields and filters.
    """
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {
            'fields': ('role',)
        }),
        ('Subscriptions (Readers Only)', {
            'fields': ('publisher_subscriptions', 'journalist_subscriptions'),
            'classes': ('collapse',),
        }),
    )
    
    filter_horizontal = ['publisher_subscriptions', 'journalist_subscriptions']
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on user role."""
        fieldsets = super().get_fieldsets(request, obj)
        
        # Hide subscription fields for non-readers
        if obj and obj.role != User.Role.READER:
            # Remove subscription fieldsets
            fieldsets = tuple(fs for fs in fieldsets if 'Subscriptions' not in fs[0])
        
        return fieldsets


class ArticleInline(admin.TabularInline):
    """Inline editor for articles in Publisher admin."""
    model = Article
    extra = 0
    fields = ['title', 'author', 'is_approved', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


class NewsletterInline(admin.TabularInline):
    """Inline editor for newsletters in Publisher admin."""
    model = Newsletter
    extra = 0
    fields = ['title', 'author', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Custom admin for Publisher model.
    
    Includes inline editors for articles and newsletters.
    """
    
    list_display = ['name', 'created_at', 'article_count', 'newsletter_count', 'editor_count', 'journalist_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['editors', 'journalists']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Staff', {
            'fields': ('editors', 'journalists'),
            'description': 'Assign editors and journalists to this publisher.'
        }),
    )
    
    inlines = [ArticleInline, NewsletterInline]
    
    def article_count(self, obj):
        """Display count of articles for this publisher."""
        count = obj.articles.count()
        if count > 0:
            url = reverse('admin:news_article_changelist') + f'?publisher__id__exact={obj.id}'
            return format_html('<a href="{}">{} articles</a>', url, count)
        return '0 articles'
    article_count.short_description = 'Articles'
    
    def newsletter_count(self, obj):
        """Display count of newsletters for this publisher."""
        return obj.newsletters.count()
    newsletter_count.short_description = 'Newsletters'
    
    def editor_count(self, obj):
        """Display count of editors for this publisher."""
        return obj.editors.count()
    editor_count.short_description = 'Editors'
    
    def journalist_count(self, obj):
        """Display count of journalists for this publisher."""
        return obj.journalists.count()
    journalist_count.short_description = 'Journalists'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Custom admin for Article model.
    
    Includes custom actions for bulk approval and filtering.
    """
    
    list_display = ['title', 'author', 'publisher', 'is_approved', 'approved_by', 'created_at', 'article_link']
    list_filter = ['is_approved', 'publisher', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    readonly_fields = ['created_at', 'updated_at', 'approved_by']
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'content')
        }),
        ('Author & Publisher', {
            'fields': ('author', 'publisher')
        }),
        ('Approval Status', {
            'fields': ('is_approved', 'approved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['approve_articles', 'reject_articles']
    
    def approve_articles(self, request, queryset):
        """
        Custom action to bulk approve articles.
        
        Sets is_approved to True and approved_by to the current admin user.
        """
        count = queryset.update(is_approved=True, approved_by=request.user)
        self.message_user(request, f'{count} articles have been approved.')
    approve_articles.short_description = 'Approve selected articles'
    
    def reject_articles(self, request, queryset):
        """
        Custom action to bulk reject articles.
        
        Sets is_approved to False and clears approved_by.
        """
        count = queryset.update(is_approved=False, approved_by=None)
        self.message_user(request, f'{count} articles have been rejected.')
    reject_articles.short_description = 'Reject selected articles'
    
    def article_link(self, obj):
        """Display link to view article on site."""
        if obj.pk:
            url = reverse('news:article_detail', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">View</a>', url)
        return '-'
    article_link.short_description = 'View on Site'
    
    def save_model(self, request, obj, form, change):
        """Override save to set approved_by when approving."""
        if obj.is_approved and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Custom admin for Newsletter model.
    """
    
    list_display = ['title', 'author', 'publisher', 'created_at']
    list_filter = ['publisher', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Newsletter Information', {
            'fields': ('title', 'content')
        }),
        ('Author & Publisher', {
            'fields': ('author', 'publisher')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )


# Customize admin site header and title
admin.site.site_header = 'News Portal Administration'
admin.site.site_title = 'News Portal Admin'
admin.site.index_title = 'Welcome to News Portal Administration'
