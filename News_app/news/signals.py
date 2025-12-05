"""
Signal handlers for the news application.

This module contains Django signals for handling article approval
and sending notifications via email and Twitter/X.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import requests
from requests.auth import HTTPBasicAuth
import base64

from .models import Article

logger = logging.getLogger('news')


@receiver(pre_save, sender=Article)
def track_approval_status(sender, instance, **kwargs):
    """
    Track the previous approval status before saving.
    
    Stores the previous is_approved value in a temporary attribute
    so we can detect changes in the post_save signal.
    """
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            instance._previous_is_approved = old_instance.is_approved
        except Article.DoesNotExist:
            instance._previous_is_approved = False
    else:
        instance._previous_is_approved = False


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """
    Handle article approval by sending emails and posting to Twitter/X.
    
    When an article's is_approved status changes from False to True:
    1. Collect all subscribers (publisher subscribers + journalist subscribers)
    2. Send email notification to each subscriber
    3. Post to Twitter/X using the X API v2
    """
    # Check if article was just approved (changed from False to True)
    previous_status = getattr(instance, '_previous_is_approved', False)
    
    if instance.is_approved and not previous_status and not created:
        logger.info(f"Article '{instance.title}' was approved. Sending notifications...")
        
        # Get all subscribers
        subscribers = []
        
        # Get publisher subscribers if article has a publisher
        if instance.publisher:
            publisher_subscribers = instance.publisher.subscribers.filter(
                role='READER'
            )
            subscribers.extend(publisher_subscribers)
        
        # Get journalist subscribers
        journalist_subscribers = instance.author.subscribers.filter(
            role='READER'
        )
        subscribers.extend(journalist_subscribers)
        
        # Remove duplicates
        subscribers = list(set(subscribers))
        
        logger.info(f"Found {len(subscribers)} subscribers to notify")
        
        # Send email notifications
        if subscribers and settings.EMAIL_HOST_USER:
            try:
                send_article_notification_email(instance, subscribers)
                logger.info(f"Successfully sent email notifications to {len(subscribers)} subscribers")
            except Exception as e:
                logger.error(f"Error sending email notifications: {str(e)}", exc_info=True)
        else:
            logger.warning("No subscribers found or email not configured")
        
        # Post to Twitter/X
        if settings.TWITTER_ACCESS_TOKEN:
            try:
                post_to_twitter(instance)
                logger.info("Successfully posted to Twitter/X")
            except Exception as e:
                logger.error(f"Error posting to Twitter/X: {str(e)}", exc_info=True)
        else:
            logger.warning("Twitter credentials not configured")


def send_article_notification_email(article, subscribers):
    """
    Send email notification to subscribers about a new approved article.
    
    Args:
        article: The Article instance that was approved
        subscribers: List of User instances to notify
    """
    subject = f"New Article: {article.title}"
    
    # Create email content
    message = f"""
    A new article has been published:
    
    Title: {article.title}
    Author: {article.author.get_full_name() or article.author.username}
    Publisher: {article.publisher.name if article.publisher else 'Independent'}
    
    {article.content[:200]}...
    
    Read the full article at: http://your-domain.com/articles/{article.id}/
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email for user in subscribers if user.email]
    
    if recipient_list:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )


def post_to_twitter(article):
    """
    Post article announcement to Twitter/X using X API v2.
    
    Args:
        article: The Article instance to post about
    """
    # Prepare tweet content
    tweet_text = f"New Article: {article.title}\n\n"
    
    # Add author info
    if article.publisher:
        tweet_text += f"By {article.author.get_full_name() or article.author.username} for {article.publisher.name}\n\n"
    else:
        tweet_text += f"By {article.author.get_full_name() or article.author.username} (Independent)\n\n"
    
    # Add article link (truncate if needed to fit Twitter's character limit)
    article_url = f"http://your-domain.com/articles/{article.id}/"
    tweet_text += article_url
    
    # Twitter has a 280 character limit, truncate if necessary
    if len(tweet_text) > 280:
        max_title_length = 280 - len(tweet_text) + len(article.title)
        tweet_text = f"New Article: {article.title[:max_title_length-3]}...\n\n{article_url}"
    
    # X API v2 endpoint
    url = "https://api.twitter.com/2/tweets"
    
    # Prepare OAuth 1.0a authentication
    # Note: For production, use a proper OAuth library like requests-oauthlib
    # This is a simplified version using Bearer Token (if available)
    headers = {
        "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "text": tweet_text
    }
    
    # Alternative: Use OAuth 1.0a if Bearer token is not available
    if not settings.TWITTER_BEARER_TOKEN and settings.TWITTER_ACCESS_TOKEN:
        # For OAuth 1.0a, you would need to use requests-oauthlib
        # This is a placeholder - in production, implement proper OAuth 1.0a
        logger.warning("OAuth 1.0a not fully implemented. Please use Bearer Token or implement OAuth 1.0a properly.")
        return
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Twitter post successful: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Twitter API error: {str(e)}")
        raise


