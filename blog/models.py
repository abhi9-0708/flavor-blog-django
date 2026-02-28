import math
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class User(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('author', 'Author'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)
    is_subscribed = models.BooleanField(default=False)
    subscription_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def initials(self):
        name = self.user.get_full_name() or self.user.username
        parts = name.split()
        return ''.join(p[0].upper() for p in parts[:2])


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or emoji")

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_posts', args=[self.slug])


class Post(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('published', 'Published'))
    ACCESS_LEVEL_CHOICES = (('free', 'Free'), ('premium', 'Premium'))

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique_for_date='publish_date')
    excerpt = models.TextField(blank=True, help_text="Short summary shown on cards. Auto-generated if blank.")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    featured_image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = TaggableManager(blank=True)

    publish_date = models.DateTimeField(default=timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVEL_CHOICES, default='free')
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-publish_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    @property
    def reading_time(self):
        """Estimated reading time in minutes."""
        word_count = len(self.body.split())
        return max(1, math.ceil(word_count / 200))

    def get_excerpt(self):
        if self.excerpt:
            return self.excerpt
        # Auto-generate from body (first 160 chars)
        import re
        clean = re.sub(r'<[^>]+>', '', self.body)
        return clean[:160].rsplit(' ', 1)[0] + '...' if len(clean) > 160 else clean

    def save(self, *args, **kwargs):
        if not self.excerpt:
            self.excerpt = self.get_excerpt()
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('post', 'user')


class Bookmark(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ('-created_date',)

    def __str__(self):
        return f'{self.user.username} bookmarked {self.post.title}'