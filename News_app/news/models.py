"""
News application models.

This module contains all database models for the news portal application,
including custom User model, Publisher, Article, and Newsletter models.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    
    Supports three roles: READER, EDITOR, and JOURNALIST.
    Automatically assigns users to appropriate groups based on role.
    """
    
    class Role(models.TextChoices):
        READER = 'READER', 'Reader'
        EDITOR = 'EDITOR', 'Editor'
        JOURNALIST = 'JOURNALIST', 'Journalist'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
        help_text="User's role in the system"
    )
    
    # ManyToMany fields for READER role
    publisher_subscriptions = models.ManyToManyField(
        'Publisher',
        related_name='subscribers',
        blank=True,
        help_text="Publishers this reader subscribes to"
    )
    
    journalist_subscriptions = models.ManyToManyField(
        'User',
        related_name='subscribers',
        blank=True,
        symmetrical=False,
        limit_choices_to={'role': Role.JOURNALIST},
        help_text="Journalists this reader subscribes to"
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
    
    def clean(self):
        """
        Validate that role-specific fields are set correctly.
        
        For READER role: publisher_subscriptions and journalist_subscriptions are allowed
        For JOURNALIST role: these fields should be None/empty
        For EDITOR role: these fields should be None/empty
        """
        super().clean()
        
        if self.role == self.Role.JOURNALIST or self.role == self.Role.EDITOR:
            # Journalists and Editors should not have subscriptions
            if self.pk:  # Only check if user already exists
                if self.publisher_subscriptions.exists() or self.journalist_subscriptions.exists():
                    raise ValidationError(
                        f"{self.role}s cannot have publisher or journalist subscriptions."
                    )
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically assign user to appropriate group.
        
        Assigns permissions based on role:
        - READER: View permissions only
        - EDITOR: View, change, delete permissions
        - JOURNALIST: Add, view, change, delete permissions
        """
        # Save the user first to get a primary key (needed for ManyToMany)
        is_new = self.pk is None
        
        # Store old role if user exists
        old_role = None
        if not is_new:
            try:
                old_user = User.objects.get(pk=self.pk)
                old_role = old_user.role
            except User.DoesNotExist:
                pass
        
        # Save the user
        super().save(*args, **kwargs)
        
        # Only assign groups if user was just created or role changed
        # This prevents unnecessary database queries on every save
        if is_new or (old_role and old_role != self.role):
            # Remove user from all groups first
            self.groups.clear()
            
            # Assign to appropriate group based on role
            group_name = f"{self.role}s"  # e.g., "READERs", "EDITORs", "JOURNALISTs"
            try:
                group = Group.objects.get(name=group_name)
                self.groups.add(group)
            except Group.DoesNotExist:
                # Group doesn't exist yet, will be created by management command
                pass
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_reader(self):
        """Check if user is a reader."""
        return self.role == self.Role.READER
    
    @property
    def is_editor(self):
        """Check if user is an editor."""
        return self.role == self.Role.EDITOR
    
    @property
    def is_journalist(self):
        """Check if user is a journalist."""
        return self.role == self.Role.JOURNALIST


class Publisher(models.Model):
    """
    Publisher model representing news publishing organizations.
    
    Publishers can have multiple editors and journalists associated with them.
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the publisher"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of the publisher"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the publisher was created"
    )
    
    # ManyToMany relationships
    editors = models.ManyToManyField(
        User,
        related_name='publishers_editing',
        blank=True,
        limit_choices_to={'role': User.Role.EDITOR},
        help_text="Editors associated with this publisher"
    )
    
    journalists = models.ManyToManyField(
        User,
        related_name='publishers_writing',
        blank=True,
        limit_choices_to={'role': User.Role.JOURNALIST},
        help_text="Journalists associated with this publisher"
    )
    
    class Meta:
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Article model representing news articles.
    
    Articles can be published by a publisher or independently by journalists.
    Articles require approval from editors before being visible to readers.
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the article"
    )
    
    content = models.TextField(
        help_text="Full content of the article"
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_articles',
        limit_choices_to={'role': User.Role.JOURNALIST},
        help_text="Journalist who wrote this article"
    )
    
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        help_text="Publisher associated with this article (null for independent articles)"
    )
    
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether this article has been approved by an editor"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_articles',
        limit_choices_to={'role': User.Role.EDITOR},
        help_text="Editor who approved this article"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the article was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the article was last updated"
    )
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_independent(self):
        """Check if article is published independently (no publisher)."""
        return self.publisher is None


class Newsletter(models.Model):
    """
    Newsletter model representing periodic newsletters.
    
    Newsletters can be published by a publisher or independently by journalists.
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the newsletter"
    )
    
    content = models.TextField(
        help_text="Content of the newsletter"
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_newsletters',
        limit_choices_to={'role': User.Role.JOURNALIST},
        help_text="Journalist who created this newsletter"
    )
    
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newsletters',
        help_text="Publisher associated with this newsletter (null for independent newsletters)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the newsletter was created"
    )
    
    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_independent(self):
        """Check if newsletter is published independently (no publisher)."""
        return self.publisher is None
