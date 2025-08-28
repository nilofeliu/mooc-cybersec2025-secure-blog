# Create this file: blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Post-related URLs
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/my/', views.my_posts, name='my_posts'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    
    # Message-related URLs
    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('messages/sent/', views.messages_sent, name='messages_sent'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/send/<str:username>/', views.send_message, name='send_message_to'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
]