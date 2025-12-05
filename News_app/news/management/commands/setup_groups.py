"""
Management command to set up groups and permissions for the news portal.

This command creates three groups (Readers, Editors, Journalists) and assigns
appropriate permissions to each group based on their roles.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Newsletter


class Command(BaseCommand):
    """
    Management command to set up groups and permissions.
    
    Creates:
    - Readers group: View permissions only
    - Editors group: View, change, delete permissions
    - Journalists group: Add, view, change, delete permissions
    """
    
    help = 'Set up groups and permissions for Readers, Editors, and Journalists'

    def handle(self, *args, **options):
        """Execute the command to create groups and assign permissions."""
        
        # Get content types for Article and Newsletter
        article_content_type = ContentType.objects.get_for_model(Article)
        newsletter_content_type = ContentType.objects.get_for_model(Newsletter)
        
        # Get all permissions for Article and Newsletter
        article_permissions = Permission.objects.filter(content_type=article_content_type)
        newsletter_permissions = Permission.objects.filter(content_type=newsletter_content_type)
        
        # Create Readers group
        readers_group, created = Group.objects.get_or_create(name='READERs')
        if created:
            self.stdout.write(self.style.SUCCESS('Created READERs group'))
        else:
            self.stdout.write('READERs group already exists')
        
        # Assign view permissions to Readers
        view_article = Permission.objects.get(
            content_type=article_content_type,
            codename='view_article'
        )
        view_newsletter = Permission.objects.get(
            content_type=newsletter_content_type,
            codename='view_newsletter'
        )
        readers_group.permissions.add(view_article, view_newsletter)
        self.stdout.write(self.style.SUCCESS('Assigned view permissions to READERs'))
        
        # Create Editors group
        editors_group, created = Group.objects.get_or_create(name='EDITORs')
        if created:
            self.stdout.write(self.style.SUCCESS('Created EDITORs group'))
        else:
            self.stdout.write('EDITORs group already exists')
        
        # Assign view, change, delete permissions to Editors
        for perm in article_permissions.filter(codename__in=['view_article', 'change_article', 'delete_article']):
            editors_group.permissions.add(perm)
        for perm in newsletter_permissions.filter(codename__in=['view_newsletter', 'change_newsletter', 'delete_newsletter']):
            editors_group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS('Assigned view, change, delete permissions to EDITORs'))
        
        # Create Journalists group
        journalists_group, created = Group.objects.get_or_create(name='JOURNALISTs')
        if created:
            self.stdout.write(self.style.SUCCESS('Created JOURNALISTs group'))
        else:
            self.stdout.write('JOURNALISTs group already exists')
        
        # Assign add, view, change, delete permissions to Journalists
        for perm in article_permissions.filter(codename__in=['add_article', 'view_article', 'change_article', 'delete_article']):
            journalists_group.permissions.add(perm)
        for perm in newsletter_permissions.filter(codename__in=['add_newsletter', 'view_newsletter', 'change_newsletter', 'delete_newsletter']):
            journalists_group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS('Assigned add, view, change, delete permissions to JOURNALISTs'))
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully set up all groups and permissions!'))


