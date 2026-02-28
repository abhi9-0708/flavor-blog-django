from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/new/', login_required(views.PostCreateView.as_view()), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/update/', login_required(views.PostUpdateView.as_view()), name='post_update'),
    path('post/<slug:slug>/delete/', login_required(views.PostDeleteView.as_view()), name='post_delete'),
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('subscribe/', login_required(views.SubscribeView.as_view()), name='subscribe'),
    path('subscribe/process/', login_required(views.process_subscription), name='process_subscription'),
    path('post/<slug:slug>/comment/', login_required(views.add_comment), name='add_comment'),
    path('api/post/<slug:slug>/like/', login_required(views.like_post), name='like_post'),
    path('api/post/<slug:slug>/bookmark/', login_required(views.toggle_bookmark), name='toggle_bookmark'),
    path('bookmarks/', login_required(views.BookmarkListView.as_view()), name='bookmarks'),
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
]