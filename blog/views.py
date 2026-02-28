from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Count
from datetime import date, timedelta

from .models import Post, Comment, Like, Profile, Category, Bookmark
from .forms import CommentForm, PostForm, CustomUserCreationForm


def custom_403(request, exception=None):
    return render(request, '403.html', status=403)


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        qs = Post.objects.filter(status='published').select_related('author', 'category').annotate(
            like_count=Count('likes'),
            comment_count=Count('comments'),
        )
        # Search
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(body__icontains=query) | Q(tags__name__icontains=query)).distinct()
        # Category filter
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category__slug=cat)
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            qs = qs.filter(tags__name__in=[tag])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['active_category'] = self.request.GET.get('category', '')
        ctx['active_tag'] = self.request.GET.get('tag', '')
        # Featured post (most viewed)
        ctx['featured_post'] = Post.objects.filter(status='published').order_by('-view_count').first()
        if self.request.user.is_authenticated:
            ctx['bookmarked_ids'] = list(Bookmark.objects.filter(user=self.request.user).values_list('post_id', flat=True))
        else:
            ctx['bookmarked_ids'] = []
        return ctx


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        Post.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.get_object()
        is_premium = getattr(self.request, 'is_premium_user', False)
        ctx['is_premium'] = is_premium
        if post.access_level == 'premium' and not is_premium and (not self.request.user.is_authenticated or post.author != self.request.user):
            ctx['paywall'] = True
            ctx['preview'] = post.body[:300] + '...'
        else:
            ctx['paywall'] = False
        ctx['comment_form'] = CommentForm()
        ctx['comments'] = post.comments.filter(parent__isnull=True).select_related('author')
        ctx['is_liked'] = self.request.user.is_authenticated and post.likes.filter(user=self.request.user).exists()
        ctx['is_bookmarked'] = self.request.user.is_authenticated and post.bookmarks.filter(user=self.request.user).exists()
        ctx['like_count'] = post.likes.count()
        # Related posts
        ctx['related_posts'] = Post.objects.filter(
            status='published', category=post.category
        ).exclude(pk=post.pk)[:3] if post.category else Post.objects.filter(status='published').exclude(pk=post.pk)[:3]
        return ctx


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        return self.request.user.role in ['author', 'admin']

    def form_valid(self, form):
        from django.utils.text import slugify
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, 'Post published successfully!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        return self.request.user == self.get_object().author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully.')
        return super().delete(request, *args, **kwargs)


class SubscribeView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/subscribe.html'


class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'blog/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 12

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post', 'post__author', 'post__category')


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'blog/profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_posts'] = Post.objects.filter(author=self.request.user, status='published')[:5]
        ctx['bookmark_count'] = Bookmark.objects.filter(user=self.request.user).count()
        ctx['post_count'] = Post.objects.filter(author=self.request.user).count()
        return ctx


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(status='published', category=self.category).select_related('author', 'category').annotate(
            like_count=Count('likes'), comment_count=Count('comments'),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0)
        ctx['active_category'] = self.category.slug
        ctx['search_query'] = ''
        ctx['active_tag'] = ''
        ctx['featured_post'] = None
        if self.request.user.is_authenticated:
            ctx['bookmarked_ids'] = list(Bookmark.objects.filter(user=self.request.user).values_list('post_id', flat=True))
        else:
            ctx['bookmarked_ids'] = []
        return ctx


@login_required
@require_POST
def process_subscription(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.is_subscribed = True
    profile.subscription_end_date = date.today() + timedelta(days=30)
    profile.save()
    messages.success(request, f"Subscribed until {profile.subscription_end_date:%b %d, %Y}")
    return redirect('post_list')


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user
        c.save()
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            cl = get_channel_layer()
            async_to_sync(cl.group_send)(f'comments_{slug}', {
                'type': 'comment_message',
                'comment': {
                    'author': c.author.username,
                    'body': c.body,
                    'created_date': c.created_date.strftime('%b %d, %Y, %I:%M %p'),
                }
            })
        except Exception:
            pass
    return redirect('post_detail', slug=slug)


@login_required
@require_POST
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})


@login_required
@require_POST
def toggle_bookmark(request, slug):
    post = get_object_or_404(Post, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(post=post, user=request.user)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})

