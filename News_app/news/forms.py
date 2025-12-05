"""
Forms for the news application.

This module contains Django forms for user registration,
article creation/editing, and other user interactions.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Article, Newsletter, Publisher

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form with role selection.
    
    Extends UserCreationForm to include role field and
    proper handling of role-specific fields.
    """
    
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        help_text="Select your role in the system"
    )
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields more user-friendly
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Additional validation can be added here
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with selected role."""
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles.
    
    Used by journalists to create and edit their articles.
    """
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your article content here...'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with user context."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit publisher choices to those the journalist is associated with
        if self.user and self.user.is_journalist:
            self.fields['publisher'].queryset = Publisher.objects.filter(
                journalists=self.user
            ) | Publisher.objects.none()
            # Add option for independent publishing
            self.fields['publisher'].required = False
            self.fields['publisher'].empty_label = "Independent (No Publisher)"
    
    def clean(self):
        """Validate article data."""
        cleaned_data = super().clean()
        
        # Ensure user is a journalist
        if self.user and not self.user.is_journalist:
            raise forms.ValidationError("Only journalists can create articles.")
        
        return cleaned_data


class NewsletterForm(forms.ModelForm):
    """
    Form for creating newsletters.
    
    Used by journalists to create newsletters.
    """
    
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter newsletter title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your newsletter content here...'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with user context."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit publisher choices to those the journalist is associated with
        if self.user and self.user.is_journalist:
            self.fields['publisher'].queryset = Publisher.objects.filter(
                journalists=self.user
            ) | Publisher.objects.none()
            self.fields['publisher'].required = False
            self.fields['publisher'].empty_label = "Independent (No Publisher)"


class SubscriptionForm(forms.Form):
    """
    Form for managing subscriptions.
    
    Allows readers to subscribe/unsubscribe from publishers and journalists.
    """
    
    publisher_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    journalist_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    action = forms.ChoiceField(
        choices=[('subscribe', 'Subscribe'), ('unsubscribe', 'Unsubscribe')],
        widget=forms.HiddenInput()
    )


