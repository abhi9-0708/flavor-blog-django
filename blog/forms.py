from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment


FIELD_CLASSES = 'w-full block rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 transition-all duration-200 focus:bg-white dark:focus:bg-gray-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:outline-none'
SELECT_CLASSES = 'w-full block rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3 text-gray-800 dark:text-gray-100 transition-all duration-200 focus:bg-white dark:focus:bg-gray-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:outline-none'


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the blank '-------' option from role dropdown
        self.fields['role'].choices = User.ROLE_CHOICES
        self.fields['role'].help_text = 'Choose Author if you want to write posts, or Reader to browse content.'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = SELECT_CLASSES
            else:
                field.widget.attrs['class'] = FIELD_CLASSES
            field.widget.attrs['placeholder'] = field.label


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'body', 'featured_image', 'category', 'tags', 'status', 'access_level']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': FIELD_CLASSES,
                'placeholder': 'Enter a compelling title...',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': FIELD_CLASSES,
                'placeholder': 'Write a short summary (optional, auto-generated if blank)...',
                'rows': 2,
            }),
            'body': forms.Textarea(attrs={
                'class': FIELD_CLASSES + ' min-h-[300px]',
                'placeholder': 'Write your article...',
                'rows': 12,
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 transition-all',
            }),
            'category': forms.Select(attrs={'class': SELECT_CLASSES}),
            'status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'access_level': forms.Select(attrs={'class': SELECT_CLASSES}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full p-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-800 dark:text-gray-100 focus:bg-white dark:focus:bg-gray-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:outline-none resize-none transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500',
                'placeholder': 'Share your thoughts...',
            })
        }
        
        