"""
Views for the news application.

This module contains all view functions and classes for handling
user requests, including authentication, article management,
subscriptions, and user dashboard.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from .models import Article, Newsletter, Publisher, User
from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm, SubscriptionForm


def home(request):
    """
    Home page view displaying latest approved articles.
    
    Shows the most recent approved articles to all visitors.
    """
    articles = Article.objects.filter(is_approved=True).order_by('-created_at')[:10]
    
    context = {
        'articles': articles,
        'latest_articles': articles[:5],
    }
    
    return render(request, 'news/home.html', context)


def register(request):
    """
    User registration view with role selection.
    
    Allows new users to register and select their role
    (READER, EDITOR, or JOURNALIST).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('news:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class ArticleListView(ListView):
    """
    List view for displaying all approved articles.
    
    Public view showing all approved articles with pagination.
    """
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter to show only approved articles."""
        queryset = Article.objects.filter(is_approved=True).select_related(
            'author', 'publisher', 'approved_by'
        )
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ArticleDetailView(DetailView):
    """
    Detail view for displaying a single article.
    
    Public view for approved articles, restricted for pending articles.
    """
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        """Filter queryset based on approval status and user permissions."""
        user = self.request.user
        
        if user.is_authenticated:
            # Authenticated users can see approved articles and their own articles
            if user.is_journalist:
                return Article.objects.filter(
                    Q(is_approved=True) | Q(author=user)
                ).select_related('author', 'publisher', 'approved_by')
            elif user.is_editor:
                # Editors can see all articles
                return Article.objects.all().select_related('author', 'publisher', 'approved_by')
            else:
                # Readers can only see approved articles
                return Article.objects.filter(is_approved=True).select_related(
                    'author', 'publisher', 'approved_by'
                )
        else:
            # Anonymous users can only see approved articles
            return Article.objects.filter(is_approved=True).select_related(
                'author', 'publisher', 'approved_by'
            )
    
    def get_context_data(self, **kwargs):
        """Add related articles to context."""
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Get related articles (same author or publisher)
        related_articles = Article.objects.filter(
            is_approved=True
        ).exclude(
            pk=article.pk
        ).filter(
            Q(author=article.author) | Q(publisher=article.publisher)
        )[:5]
        
        context['related_articles'] = related_articles
        return context


@login_required
@permission_required('news.add_article', raise_exception=True)
def article_create(request):
    """
    View for journalists to create new articles.
    
    Requires journalist role and add_article permission.
    """
    if not request.user.is_journalist:
        messages.error(request, 'Only journalists can create articles.')
        return redirect('news:article_list')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully! It will be reviewed by an editor.')
            return redirect('news:my_articles')
    else:
        form = ArticleForm(user=request.user)
    
    return render(request, 'news/article_form.html', {'form': form, 'action': 'Create'})


@login_required
@permission_required('news.change_article', raise_exception=True)
def article_edit(request, pk):
    """
    View for journalists to edit their own articles.
    
    Journalists can only edit their own articles.
    """
    article = get_object_or_404(Article, pk=pk)
    
    # Check if user is the author
    if article.author != request.user and not request.user.is_editor:
        messages.error(request, 'You can only edit your own articles.')
        return redirect('news:article_detail', pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            # Reset approval if article is edited
            if article.is_approved and article.author == request.user:
                article.is_approved = False
                article.approved_by = None
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('news:article_detail', pk=pk)
    else:
        form = ArticleForm(instance=article, user=request.user)
    
    return render(request, 'news/article_form.html', {'form': form, 'article': article, 'action': 'Edit'})


@login_required
@permission_required('news.view_article', raise_exception=True)
def pending_articles(request):
    """
    View for editors to see articles pending approval.
    
    Shows all unapproved articles that need editor review.
    """
    if not request.user.is_editor:
        messages.error(request, 'Only editors can view pending articles.')
        return redirect('news:home')
    
    pending = Article.objects.filter(is_approved=False).select_related(
        'author', 'publisher'
    ).order_by('-created_at')
    
    paginator = Paginator(pending, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'news/pending_articles.html', {
        'page_obj': page_obj,
        'pending_count': pending.count()
    })


@login_required
@permission_required('news.change_article', raise_exception=True)
@require_http_methods(["POST"])
def article_approve(request, pk):
    """
    View for editors to approve articles.
    
    Handles POST requests to approve articles.
    """
    if not request.user.is_editor:
        return HttpResponseForbidden('Only editors can approve articles.')
    
    article = get_object_or_404(Article, pk=pk)
    
    if article.is_approved:
        messages.warning(request, 'This article is already approved.')
    else:
        article.is_approved = True
        article.approved_by = request.user
        article.save()
        messages.success(request, f'Article "{article.title}" has been approved!')
    
    return redirect('news:pending_articles')


@login_required
def my_articles(request):
    """
    View for journalists to see their own articles.
    
    Shows all articles created by the logged-in journalist.
    """
    if not request.user.is_journalist:
        messages.error(request, 'Only journalists can view their articles.')
        return redirect('news:home')
    
    articles = Article.objects.filter(author=request.user).select_related(
        'publisher', 'approved_by'
    ).order_by('-created_at')
    
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'news/my_articles.html', {
        'page_obj': page_obj,
        'approved_count': articles.filter(is_approved=True).count(),
        'pending_count': articles.filter(is_approved=False).count(),
    })


@login_required
def dashboard(request):
    """
    User dashboard showing personalized content.
    
    For readers: Shows subscribed content
    For journalists: Shows their articles and stats
    For editors: Shows pending articles count
    """
    user = request.user
    context = {}
    
    if user.is_reader:
        # Get articles from subscribed publishers and journalists
        subscribed_publishers = user.publisher_subscriptions.all()
        subscribed_journalists = user.journalist_subscriptions.all()
        
        articles = Article.objects.filter(
            is_approved=True
        ).filter(
            Q(publisher__in=subscribed_publishers) |
            Q(author__in=subscribed_journalists)
        ).select_related('author', 'publisher').order_by('-created_at')[:20]
        
        newsletters = Newsletter.objects.filter(
            Q(publisher__in=subscribed_publishers) |
            Q(author__in=subscribed_journalists)
        ).select_related('author', 'publisher').order_by('-created_at')[:10]
        
        context.update({
            'articles': articles,
            'newsletters': newsletters,
            'subscribed_publishers': subscribed_publishers,
            'subscribed_journalists': subscribed_journalists,
        })
    
    elif user.is_journalist:
        # Show journalist's own articles and stats
        articles = Article.objects.filter(author=user).order_by('-created_at')[:10]
        newsletters = Newsletter.objects.filter(author=user).order_by('-created_at')[:10]
        
        context.update({
            'articles': articles,
            'newsletters': newsletters,
            'total_articles': Article.objects.filter(author=user).count(),
            'approved_articles': Article.objects.filter(author=user, is_approved=True).count(),
            'pending_articles': Article.objects.filter(author=user, is_approved=False).count(),
        })
    
    elif user.is_editor:
        # Show editor's pending articles count
        pending_count = Article.objects.filter(is_approved=False).count()
        context['pending_count'] = pending_count
    
    return render(request, 'news/dashboard.html', context)


@login_required
def subscribe_publisher(request, publisher_id):
    """
    View for readers to subscribe/unsubscribe from a publisher.
    
    Handles both subscription and unsubscription actions.
    """
    if not request.user.is_reader:
        messages.error(request, 'Only readers can subscribe to publishers.')
        return redirect('news:home')
    
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    action = request.GET.get('action', 'subscribe')
    
    if action == 'subscribe':
        request.user.publisher_subscriptions.add(publisher)
        messages.success(request, f'You have subscribed to {publisher.name}.')
    elif action == 'unsubscribe':
        request.user.publisher_subscriptions.remove(publisher)
        messages.success(request, f'You have unsubscribed from {publisher.name}.')
    
    return redirect('news:dashboard')


@login_required
def subscribe_journalist(request, journalist_id):
    """
    View for readers to subscribe/unsubscribe from a journalist.
    
    Handles both subscription and unsubscription actions.
    """
    if not request.user.is_reader:
        messages.error(request, 'Only readers can subscribe to journalists.')
        return redirect('news:home')
    
    journalist = get_object_or_404(User, pk=journalist_id, role=User.Role.JOURNALIST)
    action = request.GET.get('action', 'subscribe')
    
    if action == 'subscribe':
        request.user.journalist_subscriptions.add(journalist)
        messages.success(request, f'You have subscribed to {journalist.get_full_name() or journalist.username}.')
    elif action == 'unsubscribe':
        request.user.journalist_subscriptions.remove(journalist)
        messages.success(request, f'You have unsubscribed from {journalist.get_full_name() or journalist.username}.')
    
    return redirect('news:dashboard')


@login_required
def publisher_list(request):
    """
    View to list all publishers.
    
    Allows readers to browse and subscribe to publishers.
    """
    publishers = Publisher.objects.all().prefetch_related('editors', 'journalists')
    
    # Add subscription status for logged-in readers
    if request.user.is_reader:
        subscribed_publisher_ids = request.user.publisher_subscriptions.values_list('id', flat=True)
        for publisher in publishers:
            publisher.is_subscribed = publisher.id in subscribed_publisher_ids
    
    return render(request, 'news/publisher_list.html', {'publishers': publishers})


@login_required
def journalist_list(request):
    """
    View to list all journalists.
    
    Allows readers to browse and subscribe to journalists.
    """
    journalists = User.objects.filter(role=User.Role.JOURNALIST).select_related()
    
    # Add subscription status for logged-in readers
    if request.user.is_reader:
        subscribed_journalist_ids = request.user.journalist_subscriptions.values_list('id', flat=True)
        for journalist in journalists:
            journalist.is_subscribed = journalist.id in subscribed_journalist_ids
    
    return render(request, 'news/journalist_list.html', {'journalists': journalists})
