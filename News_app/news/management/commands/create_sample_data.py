"""
Management command to create sample data for development and testing.

Creates sample users, publishers, articles, and newsletters for testing purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.models import Publisher, Article, Newsletter
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to create sample data.
    
    Creates:
    - Sample users (readers, editors, journalists)
    - Sample publishers
    - Sample articles (approved and pending)
    - Sample newsletters
    """
    
    help = 'Create sample data for development and testing'

    def handle(self, *args, **options):
        """Execute the command to create sample data."""
        
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        self.stdout.write('Creating users...')
        
        # Create readers
        reader1, _ = User.objects.get_or_create(
            username='reader1',
            defaults={
                'email': 'reader1@example.com',
                'role': User.Role.READER,
                'first_name': 'John',
                'last_name': 'Reader',
            }
        )
        if not reader1.check_password('reader123'):
            reader1.set_password('reader123')
            reader1.save()
        
        reader2, _ = User.objects.get_or_create(
            username='reader2',
            defaults={
                'email': 'reader2@example.com',
                'role': User.Role.READER,
                'first_name': 'Jane',
                'last_name': 'Doe',
            }
        )
        if not reader2.check_password('reader123'):
            reader2.set_password('reader123')
            reader2.save()
        
        # Create editors
        editor1, _ = User.objects.get_or_create(
            username='editor1',
            defaults={
                'email': 'editor1@example.com',
                'role': User.Role.EDITOR,
                'first_name': 'Alice',
                'last_name': 'Editor',
            }
        )
        if not editor1.check_password('editor123'):
            editor1.set_password('editor123')
            editor1.save()
        
        editor2, _ = User.objects.get_or_create(
            username='editor2',
            defaults={
                'email': 'editor2@example.com',
                'role': User.Role.EDITOR,
                'first_name': 'Bob',
                'last_name': 'Smith',
            }
        )
        if not editor2.check_password('editor123'):
            editor2.set_password('editor123')
            editor2.save()
        
        # Create journalists
        journalist1, _ = User.objects.get_or_create(
            username='journalist1',
            defaults={
                'email': 'journalist1@example.com',
                'role': User.Role.JOURNALIST,
                'first_name': 'Charlie',
                'last_name': 'Reporter',
            }
        )
        if not journalist1.check_password('journalist123'):
            journalist1.set_password('journalist123')
            journalist1.save()
        
        journalist2, _ = User.objects.get_or_create(
            username='journalist2',
            defaults={
                'email': 'journalist2@example.com',
                'role': User.Role.JOURNALIST,
                'first_name': 'Diana',
                'last_name': 'Writer',
            }
        )
        if not journalist2.check_password('journalist123'):
            journalist2.set_password('journalist123')
            journalist2.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created users: {User.objects.count()}'))
        
        # Create publishers
        self.stdout.write('Creating publishers...')
        
        publisher1, _ = Publisher.objects.get_or_create(
            name='Tech News Daily',
            defaults={
                'description': 'Your daily source for technology news and updates.',
            }
        )
        publisher1.editors.add(editor1)
        publisher1.journalists.add(journalist1)
        
        publisher2, _ = Publisher.objects.get_or_create(
            name='World News Network',
            defaults={
                'description': 'Global news coverage from around the world.',
            }
        )
        publisher2.editors.add(editor2)
        publisher2.journalists.add(journalist2)
        
        self.stdout.write(self.style.SUCCESS(f'Created publishers: {Publisher.objects.count()}'))
        
        # Create articles
        self.stdout.write('Creating articles...')
        
        article1, _ = Article.objects.get_or_create(
            title='Breaking: New AI Technology Revolutionizes Healthcare',
            defaults={
                'content': 'In a groundbreaking development, researchers have unveiled a new AI system that can diagnose diseases with unprecedented accuracy. This technology promises to transform healthcare delivery worldwide.',
                'author': journalist1,
                'publisher': publisher1,
                'is_approved': True,
                'approved_by': editor1,
            }
        )
        
        article2, _ = Article.objects.get_or_create(
            title='Climate Summit Reaches Historic Agreement',
            defaults={
                'content': 'World leaders have reached a historic agreement on climate action at the latest international summit. The agreement includes ambitious targets for carbon reduction and renewable energy adoption.',
                'author': journalist2,
                'publisher': publisher2,
                'is_approved': True,
                'approved_by': editor2,
            }
        )
        
        article3, _ = Article.objects.get_or_create(
            title='Independent Journalism: The Future of News',
            defaults={
                'content': 'This article explores the growing trend of independent journalism and how it is reshaping the media landscape. Written independently by a journalist.',
                'author': journalist1,
                'publisher': None,
                'is_approved': False,
            }
        )
        
        article4, _ = Article.objects.get_or_create(
            title='Pending Review: Local Elections Update',
            defaults={
                'content': 'This article is pending editor approval. It covers the latest updates from local elections.',
                'author': journalist2,
                'publisher': publisher2,
                'is_approved': False,
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created articles: {Article.objects.count()}'))
        
        # Create newsletters
        self.stdout.write('Creating newsletters...')
        
        newsletter1, _ = Newsletter.objects.get_or_create(
            title='Weekly Tech Roundup - Week 1',
            defaults={
                'content': 'This week in tech: AI breakthroughs, new smartphone releases, and cybersecurity updates. Stay informed with our weekly roundup.',
                'author': journalist1,
                'publisher': publisher1,
            }
        )
        
        newsletter2, _ = Newsletter.objects.get_or_create(
            title='Independent Newsletter - Issue 1',
            defaults={
                'content': 'An independent newsletter covering various topics from an independent journalist perspective.',
                'author': journalist2,
                'publisher': None,
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created newsletters: {Newsletter.objects.count()}'))
        
        # Set up subscriptions
        self.stdout.write('Setting up subscriptions...')
        reader1.publisher_subscriptions.add(publisher1)
        reader1.journalist_subscriptions.add(journalist1)
        reader2.publisher_subscriptions.add(publisher2)
        reader2.journalist_subscriptions.add(journalist2)
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully created all sample data!'))
        self.stdout.write(self.style.SUCCESS('\nSample login credentials:'))
        self.stdout.write('  Readers: reader1/reader123, reader2/reader123')
        self.stdout.write('  Editors: editor1/editor123, editor2/editor123')
        self.stdout.write('  Journalists: journalist1/journalist123, journalist2/journalist123')


