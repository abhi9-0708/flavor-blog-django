from django.contrib import admin
from .models import User, Profile, Category, Post, Comment, Like, Bookmark

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_subscribed', 'subscription_end_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'access_level', 'publish_date', 'view_count')
    list_filter = ('status', 'access_level', 'author', 'category')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_date')
    list_filter = ('created_date',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date')
    list_filter = ('created_date',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_date')
    list_filter = ('created_date',)